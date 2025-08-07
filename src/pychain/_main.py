from collections.abc import Callable, Iterable

from ._compilers import TypedLambda, TypeTracker
from ._expressions import Expr, Iter, Struct


def expr[T](dtype: type[T]) -> Expr[T, T]:
    tracker = TypeTracker(p_type=dtype, r_type=dtype)
    return Expr([], tracker)


def iter[T](dtype: type[T]) -> Iter[T, T]:
    tracker = TypeTracker(p_type=Iterable[dtype], r_type=Iterable[dtype])
    return Iter([], tracker)


def struct[K, V](ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]:
    tracker = TypeTracker(p_type=dict[ktype, vtype], r_type=dict[ktype, vtype])
    return Struct([], tracker)


class LambdaBuilder[P, R]:
    __slots__ = ("_p_type", "_r_type")

    def __init__(self, p_type: type[P]) -> None:
        self._p_type: type[P] = p_type
        self._r_type = p_type

    def returns[T](self, r_type: type[T]) -> "LambdaBuilder[P, T]":
        self._r_type = r_type
        return self  # type: ignore[return-value]

    def do(self, func: Callable[[P], R]) -> TypedLambda[P, R]:
        return TypedLambda(func, self._p_type, self._r_type)  # type: ignore[return-value]


def fn[T](p_type: type[T]) -> LambdaBuilder[T, T]:
    return LambdaBuilder(p_type)
