import ast
import hashlib
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ._protocols import (
    BUILTIN_NAMES,
    INLINEABLE_BUILTINS,
    Func,
    Names,
    Operation,
    Scope,
    is_placeholder,
    CallableAst,
)

def get_func_name(final_expr_ast: ast.expr):
    temp_body_source = ast.unparse(final_expr_ast)
    source_hash = hashlib.sha256(temp_body_source.encode()).hexdigest()[:16]
    return f"{Names.PC_FUNC_.value}{source_hash}"

def get_module_ast(func_name: str, final_expr_ast: ast.expr) -> ast.Module:
    func_args = ast.arguments(args=[ast.arg(arg=Names.ARG.value)], defaults=[])
    func_def = ast.FunctionDef(
        name=func_name,
        args=func_args,
        body=[ast.Return(value=final_expr_ast)],
        decorator_list=[],
    )
    return ast.fix_missing_locations(ast.Module(body=[func_def], type_ignores=[]))

def add_cfunc(func_def: ast.FunctionDef) -> str:
    decorator = ast.Name(id="cython.cfunc", ctx=ast.Load())
    func_def.decorator_list.insert(0, decorator)
    ast.fix_missing_locations(func_def)
    return ast.unparse(func_def)


def match_node(node: CallableAst, name: str) -> ast.FunctionDef | None:
    func_def: ast.FunctionDef | None = None
    match node:
        case ast.Lambda() as lambda_node:
            func_def = lambda_to_func(lambda_node, name)
        case ast.FunctionDef() as func_def_node:
            func_def_node.name = name
            func_def = func_def_node
    return func_def


def lambda_to_func(lambda_node: ast.Lambda, name: str) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=name,
        args=lambda_node.args,
        body=[ast.Return(value=lambda_node.body)],
        decorator_list=[],
    )


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


def _extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
    if len(func_ast.body) == 1 and isinstance(stmt := func_ast.body[0], ast.Return):
        return stmt.value
    return None


def get_callable_ast(func: Callable[..., Any]) -> CallableAst | None:
    try:
        raw_source = textwrap.dedent(inspect.getsource(func)).strip()
        source_to_parse = (
            f"{Names.DUMMY.value}{raw_source}"
            if raw_source.startswith((".", "["))
            else raw_source
        )
        tree = ast.parse(source_to_parse)

        lambda_finder = LambdaFinder()
        lambda_finder.visit(tree)
        if lambda_node := lambda_finder.found_lambda:
            return lambda_node

        func_def_finder = FunctionDefFinder()
        func_def_finder.visit(tree)
        return func_def_finder.found_func

    except (TypeError, OSError, SyntaxError):
        return None


@dataclass(slots=True, frozen=True)
class ScopeManager:
    scope: Scope = field(default_factory=dict[str, Any])

    def __getitem__(self, key: str) -> Any:
        return self.scope[key]

    def clear(self) -> None:
        self.scope.clear()

    def populate_from_callable(self, func: Callable[..., Any]) -> None:
        if func.__closure__:
            for var_name, cell in zip(func.__code__.co_freevars, func.__closure__):
                self.scope[var_name] = cell.cell_contents
        for name in func.__code__.co_names:
            if name in func.__globals__ and name not in BUILTIN_NAMES:
                self.scope[name] = func.__globals__[name]

    def value_to_ast(self, value: Any) -> ast.expr:
        match value:
            case Func() as func_obj:  # type: ignore
                stable_id = hashlib.sha256(func_obj.source_code.encode()).hexdigest()[
                    :16
                ]
                base_name = Names.FUNC.value
                var_name = f"{Names.REF_.value}{base_name}_{stable_id}"
                self.scope[var_name] = func_obj
                return ast.Name(id=var_name, ctx=ast.Load())
            case bool() | int() | float() | str() | None:
                return ast.Constant(value)
            case _ if value in INLINEABLE_BUILTINS:
                return ast.Name(id=value.__name__, ctx=ast.Load())
            case _:
                base_name = getattr(value, "__name__", Names.FUNC.value)
                if not base_name.isidentifier() or base_name == "<lambda>":
                    base_name = Names.FUNC.value
                try:
                    source = inspect.getsource(value)
                    stable_id = hashlib.sha256(source.encode()).hexdigest()[:16]
                except (TypeError, OSError):
                    stable_id = id(value)
                var_name = f"{Names.REF_.value}{base_name}_{stable_id}"
                self.scope[var_name] = value
                return ast.Name(id=var_name, ctx=ast.Load())

    def resolve_placeholder_ast(self, value: Any, prev_ast: ast.expr) -> ast.expr:
        return prev_ast if is_placeholder(value) else self.value_to_ast(value)

    def try_inline_call(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr | None:
        is_simple_call = all(is_placeholder(arg) for arg in op.args) and not op.kwargs
        if not is_simple_call:
            return None

        if not (node := get_callable_ast(op.func)):
            return None

        match node:
            case ast.Lambda(args=lambda_args):
                if len(lambda_args.args) == 1:
                    self.populate_from_callable(op.func)
                    arg_name = lambda_args.args[0].arg
                    return NodeReplacer(arg_name, prev_ast).visit(node.body)

            case ast.FunctionDef(args=func_args) as func_ast:
                if len(func_args.args) == 1:
                    self.populate_from_callable(op.func)
                    if return_expr := _extract_return_expression(func_ast):
                        arg_name = func_args.args[0].arg
                        return NodeReplacer(arg_name, prev_ast).visit(return_expr)

        return None

    def build_operation_ast(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr:
        if inlined_ast := self.try_inline_call(op, prev_ast):
            return inlined_ast
        func_node = self.value_to_ast(op.func)
        args_nodes = [self.resolve_placeholder_ast(arg, prev_ast) for arg in op.args]
        kwargs_nodes = [
            ast.keyword(arg=k, value=self.resolve_placeholder_ast(v, prev_ast))
            for k, v in op.kwargs.items()
        ]
        return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)
