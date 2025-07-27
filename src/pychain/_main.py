from ._expressions._exprs import Expr
from ._expressions._iter import Iter
from ._expressions._struct import Struct
from ._tracker import TypeTracker
from ._proxy import Proxy
from collections.abc import Iterable


def proxy[T](obj: type[T]) -> T:
    return Proxy()  # type: ignore


class StructConstructor:
    def __call__[K, V](self, ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]:
        tracker = TypeTracker(p_type=dict[ktype, vtype], r_type=dict[ktype, vtype])
        return Struct([], tracker)


class ExprConstructor:
    def __call__[T](self, dtype: type[T]) -> Expr[T, T]:
        tracker = TypeTracker(p_type=dtype, r_type=dtype)
        return Expr([], tracker)


class IterConstructor:
    def __call__[T](self, dtype: type[T]) -> Iter[T, T]:
        tracker = TypeTracker(p_type=Iterable[dtype], r_type=Iterable[dtype])
        return Iter([], tracker)


expr = ExprConstructor()
iter = IterConstructor()
struct = StructConstructor()
Int = proxy(int)
Float = proxy(float)
Str = proxy(str)
