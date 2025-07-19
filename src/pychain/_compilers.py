import ast
import inspect
import uuid
from collections.abc import Callable
from typing import Any

from ._obj_exprs import ObjExpr
from ._protocols import INLINEABLE_BUILTINS, CompileResult


def collect_scope[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    func_scope: dict[str, Any] = {}
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


def collect_ast[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    final_expr_ast = ast.Name(id="arg", ctx=ast.Load())
    func_scope: dict[str, Any] = {}

    for i, func in enumerate(_pipeline):
        if func in INLINEABLE_BUILTINS:
            final_expr_ast = _from_builtin(func, final_expr_ast)
            continue

        if isinstance(func, ObjExpr):
            final_expr_ast: ast.expr = func.to_ast(final_expr_ast, func_scope)
            continue

        try:
            final_expr_ast = _get_final_ast(func, final_expr_ast)

        except (TypeError, OSError):
            final_expr_ast = _fallback(func_scope, func, i, final_expr_ast)
    return _finalize(final_expr_ast, func_scope)


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


class InlineTransformer(ast.NodeTransformer):
    def __init__(self, arg_name: str, replacement_node: ast.AST) -> None:
        self.arg_name: str = arg_name
        self.replacement_node: ast.AST = replacement_node

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id == self.arg_name:
            return self.replacement_node
        return node


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