import ast
import uuid
from enum import IntEnum, auto
from typing import Any, NamedTuple, Self, TypeGuard


class OpType(IntEnum):
    ATTR = auto()
    CALL = auto()


class OpInfo(NamedTuple):
    type: OpType
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = {}


def _arg_to_ast(arg: Any, scope: dict[str, Any]) -> ast.expr:
    if isinstance(arg, (str, int, float, bool, type(None))):
        return ast.Constant(value=arg)
    else:
        var_name: str = f"__arg_{str(uuid.uuid4()).replace('-', '')[:8]}"
        scope[var_name] = arg
        return ast.Name(id=var_name, ctx=ast.Load())


class ObjExpr:
    __slots__ = ("_operations", "__pychain_expr__")

    def __init__(self) -> None:
        self._operations: list[OpInfo] = []
        self.__pychain_expr__ = True

    def __getattr__(self, name: str) -> Self:
        self._operations.append(OpInfo(OpType.ATTR, name))
        return self

    def __call__(self, *args: Any, **kwargs: Any):
        last_op = self._operations[-1]
        self._operations[-1] = OpInfo(OpType.CALL, last_op.name, args, kwargs)
        return self

    def to_ast(self, input_node: ast.expr, func_scope: dict[str, Any]) -> ast.expr:
        current_node: ast.expr = input_node
        for op in self._operations:
            attr_node = ast.Attribute(value=current_node, attr=op.name, ctx=ast.Load())
            if op.type == OpType.ATTR:
                current_node = attr_node
            else:
                current_node = ast.Call(
                    func=attr_node,
                    args=[_arg_to_ast(arg, func_scope) for arg in op.args],
                    keywords=[
                        ast.keyword(arg=k, value=_arg_to_ast(v, func_scope))
                        for k, v in op.kwargs.items()
                    ],
                )
        return current_node


def as_expr[T](target_type: type[T]) -> T:
    """
    Create an instance of ObjExpr that can be used to build expressions.

    You can wrap any class with this function, but it's only useful for classes that have methods or attributes you want to chain.
    """
    return ObjExpr()  # type: ignore


def is_obj_expr(val: Any) -> TypeGuard[ObjExpr]:
    return getattr(val, "__pychain_expr__", False)
