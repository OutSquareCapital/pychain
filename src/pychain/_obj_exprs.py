import ast
import uuid
from typing import Any, Self, TypeGuard, override

from ._protocols import Scope


def _value_to_ast(value: Any, scope: Scope) -> ast.expr:
    match value:
        case str() | int() | float() | bool() | None:
            return ast.Constant(value=value)
        case ObjExpr():
            return value.to_ast(scope)
        case _:
            var_name = f"__arg_{str(uuid.uuid4()).replace('-', '')[:8]}"
            scope[var_name] = value
            return ast.Name(id=var_name, ctx=ast.Load())


class ObjExpr:
    __slots__ = ("_node", "_scope", "__pychain_expr__")

    def __init__(self, node: ast.expr | None = None) -> None:
        self._node: ast.expr = (
            node if node is not None else ast.Name(id="arg", ctx=ast.Load())
        )
        self._scope: dict[str, Any] = {}
        self.__pychain_expr__ = True

    def _new_node(self, node: ast.expr, scope: Scope) -> Self:
        new_instance = self.__class__(node)
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

    def to_ast(self, func_scope: Scope) -> ast.expr:
        func_scope.update(self._scope)
        return self._node

    def __getattr__(self, name: str) -> Self:
        new_node = ast.Attribute(value=self._node, attr=name, ctx=ast.Load())
        return self.__class__(new_node)

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


def as_expr[T](obj: type[T]) -> T:
    """
    Create an instance of ObjExpr that can be used to build expressions.

    You can wrap any class with this function, and it will act as if it was an instance of this type.
    """
    return ObjExpr()  # type: ignore


def is_obj_expr(val: Any) -> TypeGuard[ObjExpr]:
    return getattr(val, "__pychain_expr__", False)
