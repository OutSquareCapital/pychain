from ._exprs import Expr
from ._iter import Iter
from ._struct import Struct


class StructConstructor:
    def __call__[K, V](self, ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]:
        return Struct([])


class ExprConstructor:
    def __call__[T](self, dtype: type[T]) -> Expr[T, T]:
        return Expr([])


class IterConstructor:
    def __call__[T](self, dtype: type[T]) -> Iter[T, T]:
        return Iter([])


def as_expr[T](obj: type[T]) -> T:
    """
    Create an instance of ObjExpr that can be used to build expressions.

    You can wrap any class with this function, and it will act as if it was an instance of this type.
    """
    return Expr([])  # type: ignore


expr = ExprConstructor()
iter = IterConstructor()
struct = StructConstructor()
Int: int = as_expr(int)
Float: float = as_expr(float)
String: str = as_expr(str)
