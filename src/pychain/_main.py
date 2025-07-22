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

expr = ExprConstructor()
iter = IterConstructor()
struct = StructConstructor()

Int = expr(int)
Float = expr(float)
String = expr(str)
