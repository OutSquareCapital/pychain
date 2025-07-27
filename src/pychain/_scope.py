import ast
import hashlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ._ast_parsers import (
    NodeReplacer,
    extract_return_expression,
    get_callable_ast,
    is_typed_lambda,
)
from ._protocols import (
    BUILTIN_NAMES,
    INLINEABLE_BUILTINS,
    Func,
    Names,
    Operation,
    Scope,
    is_placeholder,
)


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
                original_value = value
                if is_typed_lambda(value):
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
        return prev_ast if is_placeholder(value) else self.value_to_ast(value)

    def try_inline_call(
        self, op: Operation[Any, Any], prev_ast: ast.expr
    ) -> ast.expr | None:
        user_func = op.func
        if is_typed_lambda(user_func):
            user_func = user_func.func

        is_simple_call = all(is_placeholder(arg) for arg in op.args) and not op.kwargs
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
        func_node = self.value_to_ast(op.func)
        args_nodes = [self.resolve_placeholder_ast(arg, prev_ast) for arg in op.args]
        kwargs_nodes = [
            ast.keyword(arg=k, value=self.resolve_placeholder_ast(v, prev_ast))
            for k, v in op.kwargs.items()
        ]
        return ast.Call(func=func_node, args=args_nodes, keywords=kwargs_nodes)
