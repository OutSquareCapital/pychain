from ._structs import Struct
from ._exprs import Expr
from ._iter import Iter
from ._obj_exprs import as_expr

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
Int: int = as_expr(int)
Float: float = as_expr(float)
String: str = as_expr(str)