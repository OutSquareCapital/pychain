import ast
import uuid
from collections.abc import Callable
from typing import Any
import inspect
from . import funcs as fn
from ._protocols import (
    INLINEABLE_BUILTINS,
    CompileResult,
    Operation,
    pipe_arg,
    ProcessFunc,
    Scope,
    TransformFunc,
    is_placeholder,
)
from abc import abstractmethod, ABC


class BaseExpr[P, R](ABC):
    __slots__ = ("_pipeline",)

    def __init__(self, pipeline: list[Operation[Any, Any]]) -> None:
        self._pipeline = pipeline

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    @abstractmethod
    def _do(self, f: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def into(self, obj: Any) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def _arg(self) -> Any:
        raise NotImplementedError

    def collect(self) -> fn.Func[P, R]:
        return collect_pipeline(self._pipeline)


class Expr[P, R](BaseExpr[P, R]):
    @property
    def _arg(self):
        return pipe_arg(P)

    def _do[T](self, func: Callable[..., T], *args: Any, **kwargs: Any) -> "Expr[P, T]":
        op = Operation(func=func, args=args, kwargs=kwargs)
        return Expr(self._pipeline + [op])

    def compose(self, *fns: ProcessFunc[R]):
        expr = self
        for f in fns:
            expr = expr._do(f, pipe_arg(R))
        return expr

    def into_str(self, template: str):
        return self._do(template.format, self._arg)

    def into[T](self, obj: TransformFunc[R, T]):
        return self._do(obj, self._arg)


# ----------- compile functions -----------


class InlineTransformer(ast.NodeTransformer):
    def __init__(self, arg_name: str, replacement_node: ast.AST):
        self.arg_name = arg_name
        self.replacement_node = replacement_node

    def visit_Name(self, node: ast.Name) -> Any:
        return self.replacement_node if node.id == self.arg_name else node


def collect_pipeline[P, R](pipeline: list[Operation[Any, Any]]) -> fn.Func[Any, Any]:
    try:
        compiled_func, source_code = _collect_ast(pipeline)
    except Exception:
        compiled_func, source_code = _collect_scope(pipeline)
    return fn.Func(compiled_func, source_code)


def _collect_scope[P](pipeline: list[Operation[P, Any]]) -> CompileResult[Any]:
    func_name = _get_fn_name()

    def _compiled(arg: Any) -> Any:
        result = arg
        for op in pipeline:
            args = tuple(result if is_placeholder(item) else item for item in op.args)
            kwargs = {
                k: (result if is_placeholder(v) else v) for k, v in op.kwargs.items()
            }
            result = op.func(*args, **kwargs)
        return result

    source = f"def {func_name}(arg): # Compiled via scope fallback"
    return _compiled, source


def _collect_ast[P](pipeline: list[Operation[P, Any]]) -> CompileResult[P]:
    final_expr_ast: ast.expr = ast.Name(id="arg", ctx=ast.Load())
    func_scope: Scope = {}
    for i, op in enumerate(pipeline):
        final_expr_ast = _compile_operation_to_ast(op, func_scope, final_expr_ast, i)
    return _finalize(final_expr_ast, func_scope)


def _extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
    if len(func_ast.body) != 1:
        return None
    if isinstance(return_stmt := func_ast.body[0], ast.Return):
        return return_stmt.value
    return None


def _value_to_ast(value: Any, scope: Scope) -> ast.expr:
    match value:
        case bool() | int() | float() | str() | None:
            return ast.Constant(value)
        case _ if value in INLINEABLE_BUILTINS:
            return ast.Name(id=value.__name__, ctx=ast.Load())
        case _:
            base_name = getattr(value, "__name__", "ref")
            if not base_name.isidentifier():
                base_name = "ref"
            var_name = f"{base_name}_{id(value)}"
            scope[var_name] = value
            return ast.Name(id=var_name, ctx=ast.Load())


def _compile_operation_to_ast(
    op: Operation[Any, Any], scope: Scope, prev_ast: ast.expr, index: int
) -> ast.expr:
    is_simple_call = all(is_placeholder(arg) for arg in op.args) and not op.kwargs
    if is_simple_call:
        try:
            source = inspect.getsource(op.func)
            func_ast = ast.parse(source).body[0]
            if isinstance(func_ast, ast.FunctionDef):
                arg_name = func_ast.args.args[0].arg
                if return_expr := _extract_return_expression(func_ast):
                    return InlineTransformer(arg_name, prev_ast).visit(return_expr)
        except (TypeError, OSError, IndexError, ValueError):
            pass

    func_node = _value_to_ast(op.func, scope)
    args_nodes = [
        prev_ast if is_placeholder(arg) else _value_to_ast(arg, scope)
        for arg in op.args
    ]
    kwargs_nodes = [
        ast.keyword(
            arg=k,
            value=prev_ast if is_placeholder(v) else _value_to_ast(v, scope),
        )
        for k, v in op.kwargs.items()
    ]
    return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)


def _finalize(final_expr_ast: ast.expr, func_scope: Scope) -> CompileResult[Any]:
    func_name = _get_fn_name()
    final_func_ast = _create_func_ast(final_expr_ast, func_name)
    source_code = ast.unparse(final_func_ast)

    code_obj = compile(final_func_ast, filename="<ast>", mode="exec")
    exec(code_obj, func_scope)
    return func_scope[func_name], source_code


def _create_func_ast(final_expr_ast: ast.expr, func_name: str) -> ast.Module:
    func_def = ast.FunctionDef(
        name=func_name,
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="arg")],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[ast.Return(value=final_expr_ast)],
        decorator_list=[],
    )
    return ast.fix_missing_locations(ast.Module(body=[func_def], type_ignores=[]))


def _get_fn_name() -> str:
    return f"generated_func_{uuid.uuid4().hex}"
