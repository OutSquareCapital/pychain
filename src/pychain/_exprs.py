import ast
import inspect
import uuid
from collections.abc import Callable
from functools import partial
from typing import Any, Self, TypeGuard, overload, override

from . import funcs as fn
from ._protocols import (
    INLINEABLE_BUILTINS,
    CompileResult,
    ProcessFunc,
    Scope,
    TransformFunc,
)


class BaseExpr[P, R]:
    def __init__(
        self,
        pipeline: list[Callable[..., Any]],
        node: ast.expr | None = None,
    ) -> None:
        self._node: ast.expr = (
            node if node is not None else ast.Name(id="arg", ctx=ast.Load())
        )
        self._scope: dict[str, Any] = {}
        self.__pychain_expr__ = True
        self._pipeline = pipeline

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    def compose(self, *fns: ProcessFunc[R]):
        for op in fns:
            self._pipeline.append(op)
        return self

    def collect(self) -> fn.Func[P, R]:
        return collect_pipeline(self._pipeline)

    def to_ast(self, func_scope: Scope) -> ast.expr:
        func_scope.update(self._scope)
        return self._node

    def _new_node(self, node: ast.expr, scope: Scope) -> Self:
        new_instance = self.__class__(node=node, pipeline=self._pipeline)
        new_instance._scope = scope
        return new_instance

    def _new_scope(self) -> Scope:
        return self._scope.copy()

    def _binary_op(self, other: Any, op: ast.operator) -> Self:
        new_scope: Scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        new_node = ast.BinOp(left=self._node, op=op, right=right_node)
        return self._new_node(new_node, new_scope)

    def _reflected_binary_op(self, other: Any, op: ast.operator) -> Self:
        new_scope: Scope = self._new_scope()
        left_node = _value_to_ast(other, new_scope)
        new_node = ast.BinOp(left=left_node, op=op, right=self._node)
        return self._new_node(new_node, new_scope)

    def _compare_op(self, other: Any, op: ast.cmpop) -> Self:
        new_scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        new_node = ast.Compare(left=self._node, ops=[op], comparators=[right_node])
        return self._new_node(new_node, new_scope)

    def _logical_op(self, other: Any, op: ast.boolop) -> Self:
        new_scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        if isinstance(self._node, ast.BoolOp) and isinstance(self._node.op, type(op)):
            new_node = ast.BoolOp(op=op, values=[*self._node.values, right_node])
        else:
            new_node = ast.BoolOp(op=op, values=[self._node, right_node])
        return self._new_node(new_node, new_scope)

    def __getattr__(self, name: str) -> Self:
        new_node = ast.Attribute(value=self._node, attr=name, ctx=ast.Load())
        return self.__class__(node=new_node, pipeline=self._pipeline)

    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        new_scope: Scope = self._new_scope()
        ast_args = [_value_to_ast(arg, new_scope) for arg in args]
        ast_kwargs = [
            ast.keyword(arg=k, value=_value_to_ast(v, new_scope))
            for k, v in kwargs.items()
        ]

        new_node = ast.Call(func=self._node, args=ast_args, keywords=ast_kwargs)
        return self._new_node(new_node, new_scope)

    def __getitem__(self, key: Any) -> Self:
        new_scope = self._new_scope()
        slice_node = _value_to_ast(key, new_scope)
        new_node = ast.Subscript(value=self._node, slice=slice_node, ctx=ast.Load())
        return self._new_node(new_node, new_scope)

    def __add__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Add())

    def __sub__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Sub())

    def __mul__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Mult())

    def __truediv__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Div())

    def __radd__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Add())

    def __rsub__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Sub())

    def __rmul__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Mult())

    def __rtruediv__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Div())

    def __mod__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Mod())

    def __pow__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Pow())

    def __matmul__(self, other: Any) -> Self:
        return self._binary_op(other, ast.MatMult())

    def __rmod__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Mod())

    def __rpow__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Pow())

    def __rmatmul__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.MatMult())

    def __and__(self, other: Any) -> Self:
        return self._logical_op(other, ast.And())

    def __or__(self, other: Any) -> Self:
        return self._logical_op(other, ast.Or())

    def __xor__(self, other: Any) -> Self:
        return self._binary_op(other, ast.BitXor())

    def __lshift__(self, other: Any) -> Self:
        return self._binary_op(other, ast.LShift())

    def __rshift__(self, other: Any) -> Self:
        return self._binary_op(other, ast.RShift())

    def __rand__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitAnd())

    def __ror__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitOr())

    def __rxor__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitXor())

    def __rlshift__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.LShift())

    def __rrshift__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.RShift())

    def __lt__(self, other: Any) -> Self:  # <
        return self._compare_op(other, ast.Lt())

    def __le__(self, other: Any) -> Self:
        return self._compare_op(other, ast.LtE())

    def __gt__(self, other: Any) -> Self:
        return self._compare_op(other, ast.Gt())

    def __ge__(self, other: Any) -> Self:
        return self._compare_op(other, ast.GtE())

    @override
    def __eq__(self, other: Any) -> Self:  # type: ignore[override]
        return self._compare_op(other, ast.Eq())

    @override
    def __ne__(self, other: Any) -> Self:  # type: ignore[override]
        return self._compare_op(other, ast.NotEq())


class Expr[P, R](BaseExpr[P, R]):
    def _do[T](self, f: T) -> "Expr[P, T]":
        match f:
            case str():
                self._pipeline.append(partial(str.format, f))
            case _ if callable(f) or is_obj_expr(f):
                self._pipeline.append(f)
            case _:
                raise TypeError(
                    f"Expected a callable, an Pychain Expression,  or a string, got {type(f)}"
                )
        return self  # type: ignore

    @overload
    def into(self, obj: str) -> "Expr[P, str]": ...
    @overload
    def into[T](self, obj: TransformFunc[R, T]) -> "Expr[P, T]": ...
    @overload
    def into[T](self, obj: T) -> "Expr[P, T]": ...
    def into[T](self, obj: TransformFunc[R, T] | str | T) -> "Expr[P, Any]":
        return self._do(obj)


# ----------- compile functions -----------


class InlineTransformer(ast.NodeTransformer):
    def __init__(self, arg_name: str, replacement_node: ast.AST) -> None:
        self.arg_name: str = arg_name
        self.replacement_node: ast.AST = replacement_node

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id == self.arg_name:
            return self.replacement_node
        return node


def collect_pipeline[P](pipeline: list[Callable[[P], Any]]) -> fn.Func[P, Any]:
    try:
        compiled_func, source_code = _collect_ast(pipeline)
    except Exception as e:
        print(f"Error collecting AST: {e}")
        compiled_func, source_code = _collect_scope(pipeline)
    return fn.Func(compiled_func, source_code)


def is_obj_expr(val: Any) -> TypeGuard[BaseExpr[Any, Any]]:
    return getattr(val, "__pychain_expr__", False)


def _value_to_ast(value: Any, scope: Scope) -> ast.expr:
    match value:
        case str() | int() | float() | bool() | None:
            return ast.Constant(value=value)
        case BaseExpr():
            return value.to_ast(scope)
        case _:
            var_name = f"__arg_{str(uuid.uuid4()).replace('-', '')[:8]}"
            scope[var_name] = value
            return ast.Name(id=var_name, ctx=ast.Load())


def _collect_scope[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    func_scope: Scope = {}
    func_name: str = _get_fn_name()
    nested_expr = "arg"
    for i, func in enumerate(_pipeline):
        scope_func_name: str = f"__func_{i}"
        func_scope[scope_func_name] = func
        nested_expr: str = f"{scope_func_name}({nested_expr})"
    code_lines: list[str] = [f"def {func_name}(arg):", f"    return {nested_expr}"]

    function_code: str = "\n".join(code_lines)
    exec(function_code, globals=func_scope)

    return func_scope[func_name], function_code


def _collect_ast[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    final_expr_ast = ast.Name(id="arg", ctx=ast.Load())
    func_scope: Scope = {}

    for i, func in enumerate(_pipeline):
        final_expr_ast = _get_ast(i, func, func_scope, final_expr_ast)
    return _finalize(final_expr_ast, func_scope)


def _get_ast[P](
    i: int, func: Callable[[P], Any], func_scope: Scope, final_expr_ast: ast.expr
) -> ast.expr:
    if is_obj_expr(func):
        return func.to_ast(func_scope)
    if func in INLINEABLE_BUILTINS:
        return _from_builtin(func, final_expr_ast)
    try:
        final_expr_ast = _get_final_ast(func, final_expr_ast)

    except (TypeError, OSError):
        final_expr_ast = _fallback(func_scope, func, i, final_expr_ast)
    return final_expr_ast


def _extract_return_expression(func_source: str) -> ast.expr | None:
    tree: ast.Module = ast.parse(func_source)
    func_def: ast.stmt = tree.body[0]

    if not isinstance(func_def, ast.FunctionDef):
        raise ValueError("Provided source is not a function definition.")
    if len(func_def.body) > 1:
        raise ValueError(
            "Function is too complex to inline (contains multiple statements)."
        )
    return_stmt: ast.stmt = func_def.body[-1]
    if isinstance(return_stmt, ast.Return):
        return return_stmt.value
    raise ValueError("Function does not contain a simple return expression.")


def _from_builtin(func: Callable[..., Any], final_expr_ast: ast.expr) -> ast.Call:
    return ast.Call(
        func=ast.Name(id=func.__name__, ctx=ast.Load()),  # Utilise le vrai nom: 'float'
        args=[final_expr_ast],
        keywords=[],
    )


def _create_func_ast(final_expr_ast: ast.expr, func_name: str) -> ast.Module:
    final_func_ast = ast.Module(
        body=[
            ast.FunctionDef(
                name=func_name,
                args=ast.arguments(
                    args=[ast.arg(arg="arg")],
                    posonlyargs=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[ast.Return(value=final_expr_ast)],
                decorator_list=[],
            )
        ],
        type_ignores=[],
    )
    final_func_ast: ast.Module = ast.fix_missing_locations(final_func_ast)
    return final_func_ast


def _get_final_ast(func: Callable[..., Any], final_expr_ast: ast.expr) -> ast.Call:
    source = inspect.getsource(func)
    func_ast = ast.parse(source).body[0]

    if not isinstance(func_ast, ast.FunctionDef):
        raise TypeError("L'élément n'est pas une fonction standard.")
    current_arg_name: str = func_ast.args.args[0].arg
    return_expr_ast = _extract_return_expression(source)
    if return_expr_ast is None:
        raise ValueError("Aucune expression de return trouvée dans la fonction.")
    transformer = InlineTransformer(current_arg_name, final_expr_ast)
    return transformer.visit(return_expr_ast)


def _fallback(
    scope: dict[str, Any], func: Callable[..., Any], i: int, final_expr_ast: ast.expr
) -> ast.Call:
    scope_func_name: str = f"__func_{i}"
    scope[scope_func_name] = func
    return ast.Call(
        func=ast.Name(id=scope_func_name, ctx=ast.Load()),
        args=[final_expr_ast],
        keywords=[],
    )


def _finalize(
    final_expr_ast: ast.expr, func_scope: dict[str, Any]
) -> tuple[Callable[..., Any], str]:
    func_name: str = _get_fn_name()
    final_func_ast: ast.Module = _create_func_ast(final_expr_ast, func_name)
    source_code: str = ast.unparse(final_func_ast)
    code_obj = compile(final_func_ast, filename="<ast>", mode="exec")

    exec(code_obj, func_scope)
    return func_scope[func_name], source_code


def _get_fn_name() -> str:
    return f"generated_func_{str(uuid.uuid4()).replace('-', '')}"
