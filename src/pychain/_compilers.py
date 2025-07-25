import ast
import inspect
import textwrap
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ._ast_parsers import LambdaFinder, NodeReplacer, extract_return_expression
from ._protocols import Func, Operation, is_placeholder
from .consts import BUILTIN_NAMES, INLINEABLE_BUILTINS, Names

type CompileResult[T] = tuple[Callable[[T], Any], str]


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
                base_name = getattr(value, "__name__", Names.FUNC.value)
                if not base_name.isidentifier() or base_name == "<lambda>":
                    base_name = Names.FUNC.value
                var_name = f"{Names.REF_.value}{base_name}_{id(value)}"
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
            parsable_source = (
                f"{Names.DUMMY.value}{source}" if source.startswith(".") else source
            )
            module = ast.parse(parsable_source)
            finder = LambdaFinder()
            finder.visit(module)

            if lambda_node := finder.found_lambda:
                if len(lambda_node.args.args) == 1:
                    self.populate_from_callable(op.func)
                    arg_name = lambda_node.args.args[0].arg
                    return NodeReplacer(arg_name, prev_ast).visit(lambda_node.body)

            if len(module.body) == 1 and isinstance(
                func_ast := module.body[0], ast.FunctionDef
            ):
                self.populate_from_callable(op.func)
                if return_expr := extract_return_expression(func_ast):
                    arg_name = func_ast.args.args[0].arg
                    return NodeReplacer(arg_name, prev_ast).visit(return_expr)
        except (TypeError, OSError, IndexError, ValueError, SyntaxError):
            return None
        return None


def to_ast[P](pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
    manager = ScopeManager()
    compiled_func, source_code = _compile_logic(pipeline, manager)

    return Func(compiled_func, source_code, manager.scope)


def to_numba[P](pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
    from numba import jit

    manager = ScopeManager()
    compiled_func, source_code = _compile_logic(pipeline, manager)
    try:
        compiled_func: Callable[[P], Any] = jit(compiled_func)
    except Exception as e:
        print(f"Failed to compile function: {e}")
    return Func(compiled_func, source_code, manager.scope)


def _compile_logic[P](
    pipeline: list[Operation[P, Any]], manager: ScopeManager
) -> CompileResult[P]:
    final_expr_ast: ast.expr = ast.Name(id=Names.ARG.value, ctx=ast.Load())

    for op in pipeline:
        final_expr_ast = _build_operation_ast(op, final_expr_ast, manager)

    return _finalize(final_expr_ast, manager)


def _build_operation_ast(
    op: Operation[Any, Any], prev_ast: ast.expr, manager: ScopeManager
) -> ast.expr:
    if inlined_ast := manager.try_inline_call(op, prev_ast):
        return inlined_ast
    func_node = manager.value_to_ast(op.func)
    args_nodes = [manager.resolve_placeholder_ast(arg, prev_ast) for arg in op.args]
    kwargs_nodes = [
        ast.keyword(arg=k, value=manager.resolve_placeholder_ast(v, prev_ast))
        for k, v in op.kwargs.items()
    ]
    return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)


def _finalize(final_expr_ast: ast.expr, manager: ScopeManager) -> CompileResult[Any]:
    func_name = f"{Names.PC_FUNC_.value}{uuid.uuid4().hex}"
    func_args = ast.arguments(args=[ast.arg(arg=Names.ARG.value)], defaults=[])
    func_def = ast.FunctionDef(
        name=func_name,
        args=func_args,
        body=[ast.Return(value=final_expr_ast)],
        decorator_list=[],
    )
    module_ast = ast.fix_missing_locations(ast.Module(body=[func_def], type_ignores=[]))
    source_code = ast.unparse(module_ast)
    code_obj = compile(module_ast, filename=Names.PYCHAIN_AST.value, mode="exec")
    exec(code_obj, manager.scope)
    return manager.scope[func_name], source_code
