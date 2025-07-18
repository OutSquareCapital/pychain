import ast
import inspect
import uuid
from collections.abc import Callable
from typing import Any

def collect_pipeline[P](pipeline: list[Callable[[P], Any]]) -> Callable[[P], Any]:
        try:
            func = collect_ast(pipeline)
        except Exception as e:
            print(f"Error collecting AST: {e}")
            func = collect_scope(pipeline)
        return func

def collect_scope[P](_pipeline: list[Callable[[P], Any]]) -> Callable[[P], Any]:
    func_scope: dict[str, Any] = {}
    func_name: str = f"generated_func_{str(uuid.uuid4()).replace('-', '')}"
    nested_expr = "arg"
    for i, func in enumerate(_pipeline):
        scope_func_name: str = f"__func_{i}"
        func_scope[scope_func_name] = func
        nested_expr: str = f"{scope_func_name}({nested_expr})"
    code_lines: list[str] = [f"def {func_name}(arg):", f"    return {nested_expr}"]

    function_code: str = "\n".join(code_lines)
    exec(function_code, globals=func_scope)

    return func_scope[func_name]

def collect_ast(_pipeline: list[Callable[[Any], Any]]) -> Callable[[Any], Any]:
    final_expr_ast = ast.Name(id="arg", ctx=ast.Load())
    arg_name: str = "arg"
    func_scope: dict[str, Any] = {}

    for i, func in enumerate(_pipeline):
        try:
            source = inspect.getsource(func)
            func_ast = ast.parse(source).body[0]

            if not isinstance(func_ast, ast.FunctionDef):
                raise TypeError("L'élément n'est pas une fonction standard.")
            current_arg_name = func_ast.args.args[0].arg
            return_expr_ast = _extract_return_expression(source)
            if return_expr_ast is None:
                raise ValueError(
                    "Aucune expression de return trouvée dans la fonction."
                )
            transformer = InlineTransformer(current_arg_name, final_expr_ast)
            final_expr_ast = transformer.visit(return_expr_ast)

        except (TypeError, OSError):
            scope_func_name = f"__func_{i}"
            func_scope[scope_func_name] = func
            final_expr_ast = ast.Call(
                func=ast.Name(id=scope_func_name, ctx=ast.Load()),
                args=[final_expr_ast],
                keywords=[],
            )
    func_name: str = f"generated_func_{str(uuid.uuid4()).replace('-', '')}"

    final_func_ast = ast.Module(
        body=[
            ast.FunctionDef(
                name=func_name,
                args=ast.arguments(
                    args=[ast.arg(arg=arg_name)],
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
    code_obj = compile(final_func_ast, filename="<ast>", mode="exec")

    exec(code_obj, func_scope)
    return func_scope[func_name]

def _extract_return_expression(func_source: str) -> ast.expr | None:
    tree = ast.parse(func_source)
    # On suppose que la fonction est le premier élément du module
    func_def = tree.body[0]
    if isinstance(func_def, ast.FunctionDef):
        # On suppose que la dernière instruction est un return
        return_stmt: ast.stmt = func_def.body[-1]
        if isinstance(return_stmt, ast.Return):
            return return_stmt.value
    raise ValueError("Impossible d'extraire une expression de return simple.")


class InlineTransformer(ast.NodeTransformer):
    def __init__(self, arg_name: str, replacement_node: ast.AST) -> None:
        self.arg_name: str = arg_name
        self.replacement_node: ast.AST = replacement_node

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id == self.arg_name:
            return self.replacement_node
        return node

