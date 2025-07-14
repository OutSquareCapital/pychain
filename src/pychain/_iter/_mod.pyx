# distutils: language=c++

from collections.abc import Callable, Iterable
from random import Random
from typing import Any, TypeVar

import numpy as np
import polars as pl

from ..funcs import agg, fn, it, gp
from .._protocols import CheckFunc, ProcessFunc, TransformFunc

V = TypeVar("V")
K = TypeVar("K")

cdef class Iter:
    _value: Iterable[Any]
    _pipeline: list[Callable[[Iterable[Any]], Any]]

    def __init__(self, _value: Iterable[Any], _pipeline: list[Callable[[Iterable[Any]], Any]] | None = None):
        self._value = _value
        self._pipeline = _pipeline if _pipeline is not None else []

    def __repr__(self):
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    cdef _do(self, f: ProcessFunc[Iterable[Any]]):
        self._pipeline.append(f)
        return self

    cdef _into(self, f: TransformFunc[Iterable[Any], Iterable[Any]]):
        return self.__class__(
            _value=self._value,
            _pipeline=[fn.compose(*self._pipeline, f)],
        )

    cpdef group_by(self, on: TransformFunc[V, Any]):
        return gp.group_by(on=on)(self.unwrap())

    cpdef into_frequencies(self):
        return self._into(gp.frequencies)

    cpdef reduce_by(
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ):
        return self._into(gp.reduce_by(key=key, binop=binop))

    cpdef clone(self):
        return self.__class__(fn.clone(self._value), fn.clone(self._pipeline))

    cpdef unwrap(self):
        if not self._pipeline:
            return self._value
        return fn.pipe(self._value, *self._pipeline)


    cpdef agg(self, on: Callable[[Iterable[Any]], Any]):
        return on(self.unwrap())

    cpdef map(self, f: TransformFunc[V, Any]):
        return self._into(f=fn.partial_map(f))

    cpdef flat_map(self, f: TransformFunc[V, Iterable[Any]]):
        return self._into(f=fn.flat_map(f))

    cpdef starmap(self, f: TransformFunc[V, Any]):
        return self._into(f=it.starmap(f))

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
        return self._into(f=enumerate)

    cpdef flatten(self):
        return self._into(f=it.flatten)

    cpdef partition(self, n: int, pad: Any | None = None):
        return self._into(f=it.partition(n=n, pad=pad))

    cpdef partition_all(self, n: int):
        return self._into(f=it.partition_all(n))

    cpdef rolling(self, length: int):
        return self._into(f=it.rolling(length=length))

    cpdef cross_join(self, other: Iterable[Any]):
        return self._into(it.cross_join(other=other))

    cpdef first(self):
        return agg.first(self.unwrap())

    cpdef second(self):
        return agg.second(self.unwrap())

    cpdef last(self):
        return agg.last(self.unwrap())

    cpdef at_index(self, index: int):
        return agg.at_index(index=index)(self.unwrap())

    cpdef len(self):
        return agg.length(self.unwrap())

    cpdef to_obj(self, obj: Callable[[Iterable[Any]], Any]):
        return obj(self.unwrap())

    cpdef to_list(self):
        return list(self.unwrap())

    cpdef to_set(self):
        return set(self.unwrap())

    cpdef to_dict(self):
        return dict(enumerate(self.unwrap()))

    cpdef to_array(self):
        return np.array(self.unwrap())

    cpdef to_series(self):
        return pl.Series(self.unwrap())

    def diff(
        self,
        *others: Iterable[Any],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ):
        return self._into(f=it.diff(others=others, default=default, key=key))

    def compose(self, *fns: TransformFunc[V, Any]):
        return self._into(f=fn.compose_on_iter(*fns))

    def zip_with(
        self, *others: Iterable[Any], strict: bool = False
    ):
        return self._into(f=it.zip_with(others=others, strict=strict))

    def merge_sorted(
        self, *others: Iterable[Any], sort_on: Callable[[Any], Any] | None = None
    ):
        return self._do(f=it.merge_sorted(others=others, sort_on=sort_on))


    def interleave(self, *others: Iterable[Any]):
        return self._do(f=it.interleave(others))


    def concat(self, *others: Iterable[Any]):
        return self._do(f=it.concat(others))
