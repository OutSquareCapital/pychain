from dataclasses import dataclass
import ast
from typing import Any

@dataclass(slots=True, frozen=True)
class NodeReplacer(ast.NodeTransformer):
    arg_name: str
    replacement_node: ast.AST

    def visit_Name(self, node: ast.Name) -> Any:
        return self.replacement_node if node.id == self.arg_name else node


@dataclass(slots=True)
class LambdaFinder(ast.NodeVisitor):
    found_lambda: ast.Lambda | None = None

    def visit_Lambda(self, node: ast.Lambda) -> None:
        if self.found_lambda is None:
            self.found_lambda = node

@dataclass(slots=True)
class FunctionDefFinder(ast.NodeVisitor):
    found_func: ast.FunctionDef | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.found_func is None:
            self.found_func = node

def extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
    if len(func_ast.body) == 1 and isinstance(stmt := func_ast.body[0], ast.Return):
        return stmt.value
    return None
