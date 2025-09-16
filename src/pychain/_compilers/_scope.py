import ast
import hashlib
import inspect
from collections.abc import Callable
from typing import Any

from ._ast_parsers import (
    NodeReplacer,
    TypedLambda,
    extract_return_expression,
    get_callable_ast,
)
from ._enums import BUILTIN_NAMES, INLINEABLE_BUILTINS, Names
from ._module_builder import SourceCode
from ._protocols import (
    Func,
    Operation,
    Placeholder,
    Scope,
)


class ScopeManager:
    module: ast.Module
    func_name: str
    expr: ast.expr
    scope: Scope

    def __init__(self) -> None:
        self.scope: Scope = {}

    def __getitem__(self, key: str) -> Any:
        return self.scope[key]

    def build(self, pipeline: list[Operation[Any, Any]]):
        return (
            self.from_pipeline(pipeline)
            .get_func_name()
            .get_module_ast()
            .execute()
            .into_result()
        )

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
                original_value = value
                if TypedLambda.identity(value):
                    value = value.func
                base_name = getattr(value, "__name__", Names.FUNC.value)
                if not base_name.isidentifier() or base_name == Names.LAMBDA.value:
                    base_name = Names.FUNC.value
                try:
                    source = inspect.getsource(value)
                    stable_id = hashlib.sha256(source.encode()).hexdigest()[:16]
                except (TypeError, OSError):
                    # Fallback déterministe sur le bytecode
                    stable_id = hashlib.sha256(value.__code__.co_code).hexdigest()[:16]
                var_name = f"{Names.REF_.value}{base_name}_{stable_id}"
                self.scope[var_name] = original_value
                return ast.Name(id=var_name, ctx=ast.Load())

    def resolve_placeholder_ast(self, value: Any, prev_ast: ast.expr) -> ast.expr:
        return prev_ast if Placeholder.identity(value) else self.value_to_ast(value)

    def try_inline_call(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr | None:
        user_func = op.func
        if TypedLambda.identity(user_func):
            user_func = user_func.func
        is_simple_call = (
            all(Placeholder.identity(arg) for arg in op.args) and not op.kwargs
        )
        if not is_simple_call:
            return None
        if not (node := get_callable_ast(user_func)):
            return None
        match node:
            case ast.Lambda(args=lambda_args):
                if len(lambda_args.args) == 1:
                    self.populate_from_callable(user_func)
                    arg_name = lambda_args.args[0].arg
                    return NodeReplacer(arg_name, prev_ast).visit(node.body)
            case ast.FunctionDef(args=func_args) as func_ast:
                if len(func_args.args) == 1:
                    self.populate_from_callable(user_func)
                    if return_expr := extract_return_expression(func_ast):
                        arg_name = func_args.args[0].arg
                        return NodeReplacer(arg_name, prev_ast).visit(return_expr)
        return None

    def build_operation_ast(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr:
        if inlined_ast := self.try_inline_call(op, prev_ast):
            return inlined_ast
        return ast.Call(
            func=self.value_to_ast(op.func),
            args=[self.resolve_placeholder_ast(arg, prev_ast) for arg in op.args],
            keywords=[
                ast.keyword(arg=k, value=self.resolve_placeholder_ast(v, prev_ast))
                for k, v in op.kwargs.items()
            ],
        )

    def from_pipeline(self, pipeline: list[Operation[Any, Any]]):
        final_expr_ast: ast.expr = ast.Name(id=Names.ARG.value, ctx=ast.Load())
        for op in pipeline:
            final_expr_ast = self.build_operation_ast(op, final_expr_ast)
        self.expr = final_expr_ast
        return self

    def get_func_name(self):
        temp_body_source = ast.unparse(self.expr)
        source_hash = hashlib.sha256(temp_body_source.encode()).hexdigest()[:16]
        self.func_name = f"{Names.PC_FUNC_.value}{source_hash}"
        return self

    def get_module_ast(self):
        func_args = ast.arguments(args=[ast.arg(arg=Names.ARG.value)], defaults=[])
        func_def = ast.FunctionDef(
            name=self.func_name,
            args=func_args,
            body=[ast.Return(value=self.expr)],
            decorator_list=[],
        )
        self.module = ast.fix_missing_locations(
            ast.Module(body=[func_def], type_ignores=[])
        )
        return self

    def execute(self):
        exec(
            compile(self.module, filename=Names.PYCHAIN_AST.value, mode="exec"),
            self.scope,
        )
        return self

    def into_result(self):
        return self.scope[self.func_name], SourceCode(
            ast.unparse(self.module), self.func_name
        )
