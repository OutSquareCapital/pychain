# distutils: language=c++

from collections.abc import Callable, Iterable
from random import Random
from typing import Any, TypeVar

from ..funcs import fn, it, agg
from .._protocols import CheckFunc, ProcessFunc, TransformFunc

V = TypeVar("V")
K = TypeVar("K")

cdef class IterConstructor:
    def __call__(self, *dtype: type):
        return Iter(fn.identity)

    cpdef attr(self, name: str, dtype: type):
        return Iter(fn.attr(name))

    cpdef item(self, key: Any, dtype: type):
        return Iter(fn.item(key))

cdef class Iter:
    _pipeline: Callable[[Iterable[Any]], Any]

    def __init__(self, pipeline: Callable[[Iterable[Any]], Any]):
        self._pipeline = pipeline

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:[\n{str(self._pipeline)}\n])"

    def __call__(self, value: Any):
        return self._pipeline(value)

    def __class_getitem__(cls, key: tuple[type, ...]) -> type:
        return cls

    def _do(self, f: Callable[[Any], Any]):
        def _new_pipeline(value: Any):
            return f(self._pipeline(value))
        return self.__class__(pipeline=_new_pipeline)

    cpdef group_by(self, on: TransformFunc[V, Any]):
        return self._do(agg.group_by(on=on))

    cpdef into_frequencies(self):
        return self._do(agg.frequencies)

    cpdef reduce_by(
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ):
        return self._do(agg.reduce_by(key=key, binop=binop))

    cpdef clone(self):
        return self._do(fn.clone)

    cpdef map(self, f: TransformFunc[V, Any]):
        return self._do(f=fn.partial_map(f))

    cpdef flat_map(self, f: TransformFunc[V, Iterable[Any]]):
        return self._do(f=fn.flat_map(f))

    cpdef starmap(self, f: TransformFunc[V, Any]):
        return self._do(f=it.starmap(f))

    cpdef take_while(self, predicate: CheckFunc[V]):
        return self._do(f=it.take_while(predicate))

    cpdef drop_while(self, predicate: CheckFunc[V]):
        return self._do(f=it.drop_while(predicate))

    cpdef interpose(self, element: Any):
        return self._do(f=it.interpose(element))

    cpdef top_n(self, n: int, key: Callable[[Any], Any] | None = None):
        return self._do(f=it.top_n(n=n, key=key))

    cpdef random_sample(
        self, probability: float, state: Random | int | None = None
    ):
        return self._do(f=it.random_sample(probability=probability, state=state))

    cpdef filter(self, f: CheckFunc[V]):
        return self._do(f=fn.partial_filter(f))

    cpdef accumulate(self, f: Callable[[V, V], V]):
        return self._do(f=it.accumulate(f=f))

    cpdef insert_left(self, value: Any):
        return self._do(f=it.insert_left(value))

    cpdef peek(self, note: str | None = None):
        return self._do(f=it.peek(note=note))

    cpdef peekn(self, n: int, note: str | None = None):
        return self._do(f=it.peekn(n=n, note=note))

    cpdef head(self, n: int):
        return self._do(f=it.head(n=n))

    cpdef tail(self, n: int):
        return self._do(f=it.tail(n=n))

    cpdef drop_first(self, n: int):
        return self._do(f=it.drop_first(n=n))

    cpdef every(self, index: int):
        return self._do(f=it.every(index=index))

    cpdef repeat(self, n: int):
        return self._do(f=it.repeat(n=n))

    cpdef unique(self):
        return self._do(f=it.unique)

    cpdef cumsum(self):
        return self._do(f=it.cumsum())

    cpdef cumprod(self):
        return self._do(f=it.cumprod())

    cpdef tap(self, func: Callable[[Any], None]):
        return self._do(f=it.tap(func=func))

    cpdef enumerate(self):
        return self._do(f=enumerate)

    cpdef flatten(self):
        return self._do(f=it.flatten)

    cpdef partition(self, n: int, pad: Any | None = None):
        return self._do(f=it.partition(n=n, pad=pad))

    cpdef partition_all(self, n: int):
        return self._do(f=it.partition_all(n))

    cpdef rolling(self, length: int):
        return self._do(f=it.rolling(length=length))

    cpdef cross_join(self, other: Iterable[Any]):
        return self._do(it.cross_join(other=other))


    def diff(
        self,
        *others: Iterable[Any],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ):
        return self._do(f=it.diff(others=others, default=default, key=key))

    def compose(self, *fns: TransformFunc[V, Any]):
        return self._do(f=fn.compose_on_iter(*fns))

    def zip_with(
        self, *others: Iterable[Any], strict: bool = False
    ):
        return self._do(f=it.zip_with(others=others, strict=strict))

    def merge_sorted(
        self, *others: Iterable[Any], sort_on: Callable[[Any], Any] | None = None
    ):
        return self._do(f=it.merge_sorted(others=others, sort_on=sort_on))


    def interleave(self, *others: Iterable[Any]):
        return self._do(f=it.interleave(others))


    def concat(self, *others: Iterable[Any]):
        return self._do(f=it.concat(others))
