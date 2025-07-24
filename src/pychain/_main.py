from ._exprs import Expr
from ._iter import Iter
from ._struct import Struct


class StructConstructor:
    def __call__[K, V](self, ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]:
        specific_class = Struct[ktype, vtype, ktype, vtype]
        return specific_class([])


class ExprConstructor:
    def __call__[T](self, dtype: type[T]) -> Expr[T, T]:
        specific_class = Expr[dtype, dtype]
        return specific_class([])

class IterConstructor:
    def __call__[T](self, dtype: type[T]) -> Iter[T, T]:
        specific_class = Iter[dtype, dtype]
        return specific_class([])

expr = ExprConstructor()
iter = IterConstructor()
struct = StructConstructor()
