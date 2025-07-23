import ast
import inspect
import uuid
from collections.abc import Callable
from typing import Any

from ._protocols import Func, Operation, is_placeholder


type Scope = dict[str, Any]
type CompileResult[T] = tuple[Callable[[T], Any], str]

INLINEABLE_BUILTINS: set[type | Callable[..., Any]] = {
    int,
    str,
    float,
    list,
    dict,
    tuple,
    set,
    zip,
    enumerate,
    range,
    map,
    filter,
    reversed,
    len,
    round,
    repr,
    sum,
    max,
    min,
    abs,
    all,
    any,
    sorted,
    iter,
    next,
}


def collect_pipeline(pipeline: list[Operation[Any, Any]]) -> Func[Any, Any]:
    return Compiler().compile(pipeline)


class Compiler:
    class _InlineTransformer(ast.NodeTransformer):
        def __init__(self, arg_name: str, replacement_node: ast.AST):
            self.arg_name = arg_name
            self.replacement_node = replacement_node

        def visit_Name(self, node: ast.Name) -> Any:
            return self.replacement_node if node.id == self.arg_name else node

    def __init__(self) -> None:
        self.scope: Scope = {}

    def compile[P](self, pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
        compiled_func, source_code = self._compile_logic(pipeline)
        return Func(compiled_func, source_code)

    def _compile_logic[P](self, pipeline: list[Operation[P, Any]]) -> CompileResult[P]:
        self.scope = {}
        final_expr_ast: ast.expr = ast.Name(id="arg", ctx=ast.Load())

        for op in pipeline:
            final_expr_ast = self._build_operation_ast(op, final_expr_ast)

        return self._finalize(final_expr_ast)

    def _resolve_placeholder_ast(self, value: Any, prev_ast: ast.expr) -> ast.expr:
        return prev_ast if is_placeholder(value) else self._value_to_ast(value)

    def _build_operation_ast(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr:
        if inlined_ast := self._try_inline_call(op, prev_ast):
            return inlined_ast
        func_node = self._value_to_ast(op.func)
        args_nodes = [self._resolve_placeholder_ast(arg, prev_ast) for arg in op.args]
        kwargs_nodes = [
            ast.keyword(arg=k, value=self._resolve_placeholder_ast(v, prev_ast))
            for k, v in op.kwargs.items()
        ]

        return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)

    def _try_inline_call(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr | None:
        if op.func.__name__ == "<lambda>":
            return None
        is_simple_call = all(is_placeholder(arg) for arg in op.args) and not op.kwargs
        if not is_simple_call:
            return None
        try:
            source = inspect.getsource(op.func)
            func_ast = ast.parse(source).body[0]
            if (
                isinstance(func_ast, ast.FunctionDef)
                and (return_expr := self._extract_return_expression(func_ast))
                and func_ast.args.args
            ):
                arg_name = func_ast.args.args[0].arg
                return self._InlineTransformer(arg_name, prev_ast).visit(return_expr)
        except (TypeError, OSError, IndexError, ValueError):
            return None
        return None

    def _value_to_ast(self, value: Any) -> ast.expr:
        match value:
            case bool() | int() | float() | str() | None:
                return ast.Constant(value)
            case _ if value in INLINEABLE_BUILTINS:
                return ast.Name(id=value.__name__, ctx=ast.Load())
            case _:
                base_name = getattr(value, "__name__", "ref")
                if not base_name.isidentifier() or base_name == "<lambda>":
                    base_name = "ref"
                var_name = f"{base_name}_{id(value)}"
                self.scope[var_name] = value
                return ast.Name(id=var_name, ctx=ast.Load())

    @staticmethod
    def _extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
        if len(func_ast.body) == 1 and isinstance(stmt := func_ast.body[0], ast.Return):
            return stmt.value
        return None

    def _finalize(self, final_expr_ast: ast.expr) -> CompileResult[Any]:
        func_name = _get_fn_name()
        func_args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="arg")],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )
        func_def = ast.FunctionDef(
            name=func_name,
            args=func_args,
            body=[ast.Return(value=final_expr_ast)],
            decorator_list=[],
        )

        module_ast = ast.fix_missing_locations(
            ast.Module(body=[func_def], type_ignores=[])
        )

        source_code = ast.unparse(module_ast)
        code_obj = compile(module_ast, filename="<pychain_ast>", mode="exec")
        exec(code_obj, self.scope)

        return self.scope[func_name], source_code


def _get_fn_name() -> str:
    return f"generated_func_{uuid.uuid4().hex}"
