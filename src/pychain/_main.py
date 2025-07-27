from collections.abc import Callable, Iterable
from ._ast_parsers import TypedLambda, TypeTracker
from ._expressions._exprs import Expr
from ._expressions._iter import Iter
from ._expressions._struct import Struct


def expr[T](dtype: type[T]) -> Expr[T, T]:
    tracker = TypeTracker(p_type=dtype, r_type=dtype)
    return Expr([], tracker)


def iter[T](dtype: type[T]) -> Iter[T, T]:
    tracker = TypeTracker(p_type=Iterable[dtype], r_type=Iterable[dtype])
    return Iter([], tracker)


def struct[K, V](ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]:
    tracker = TypeTracker(p_type=dict[ktype, vtype], r_type=dict[ktype, vtype])
    return Struct([], tracker)


def fn[P, R](
    p_type: type[P], r_type: type[R], func: Callable[[P], R]
) -> TypedLambda[P, R]:
    return TypedLambda(func, p_type, r_type)
