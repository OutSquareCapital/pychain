import ast
import inspect
import textwrap
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from ._cythonifier import Func
from ._protocols import Operation, is_placeholder
from .funcs import INLINEABLE_BUILTINS, BUILTIN_NAMES

type CompileResult[T] = tuple[Callable[[T], Any], str]


def _extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
    if len(func_ast.body) == 1 and isinstance(stmt := func_ast.body[0], ast.Return):
        return stmt.value
    return None


@dataclass(slots=True, frozen=True)
class _NodeReplacer(ast.NodeTransformer):
    arg_name: str
    replacement_node: ast.AST

    def visit_Name(self, node: ast.Name) -> Any:
        return self.replacement_node if node.id == self.arg_name else node


@dataclass(slots=True)
class _LambdaFinder(ast.NodeVisitor):
    found_lambda: ast.Lambda | None = None

    def visit_Lambda(self, node: ast.Lambda) -> None:
        if self.found_lambda is None:
            self.found_lambda = node


@dataclass(slots=True, frozen=True)
class ScopeManager:
    scope: dict[str, Any] = field(default_factory=dict[str, Any])

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

    def resolve_placeholder_ast(self, value: Any, prev_ast: ast.expr) -> ast.expr:
        return prev_ast if is_placeholder(value) else self.value_to_ast(value)

    def try_inline_call(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr | None:
        is_simple_call = all(is_placeholder(arg) for arg in op.args) and not op.kwargs
        if not is_simple_call:
            return None
        try:
            source = textwrap.dedent(inspect.getsource(op.func)).strip()
            parsable_source = f"dummy{source}" if source.startswith(".") else source
            module = ast.parse(parsable_source)
            finder = _LambdaFinder()
            finder.visit(module)

            if lambda_node := finder.found_lambda:
                if len(lambda_node.args.args) == 1:
                    self.populate_from_callable(op.func)
                    arg_name = lambda_node.args.args[0].arg
                    return _NodeReplacer(arg_name, prev_ast).visit(lambda_node.body)

            if len(module.body) == 1 and isinstance(
                func_ast := module.body[0], ast.FunctionDef
            ):
                self.populate_from_callable(op.func)
                if return_expr := _extract_return_expression(func_ast):
                    arg_name = func_ast.args.args[0].arg
                    return _NodeReplacer(arg_name, prev_ast).visit(return_expr)
        except (TypeError, OSError, IndexError, ValueError, SyntaxError):
            return None
        return None


@dataclass(slots=True, frozen=True)
class Compiler:
    scope: ScopeManager = field(default_factory=ScopeManager)

    def run[P](self, pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
        self.scope.clear()
        compiled_func, source_code = self._compile_logic(pipeline)

        return Func(compiled_func, source_code)

    def _compile_logic[P](self, pipeline: list[Operation[P, Any]]) -> CompileResult[P]:
        final_expr_ast: ast.expr = ast.Name(id="arg", ctx=ast.Load())

        for op in pipeline:
            final_expr_ast = self._build_operation_ast(op, final_expr_ast)

        return self._finalize(final_expr_ast)

    def _build_operation_ast(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr:
        if inlined_ast := self.scope.try_inline_call(op, prev_ast):
            return inlined_ast
        func_node = self.scope.value_to_ast(op.func)
        args_nodes = [
            self.scope.resolve_placeholder_ast(arg, prev_ast) for arg in op.args
        ]
        kwargs_nodes = [
            ast.keyword(arg=k, value=self.scope.resolve_placeholder_ast(v, prev_ast))
            for k, v in op.kwargs.items()
        ]
        return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)

    def _finalize(self, final_expr_ast: ast.expr) -> CompileResult[Any]:
        func_name = f"generated_func_{uuid.uuid4().hex}"
        func_args = ast.arguments(args=[ast.arg(arg="arg")], defaults=[])
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
        exec(code_obj, self.scope.scope)
        return self.scope[func_name], source_code
