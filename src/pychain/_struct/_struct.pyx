# distutils: language=c++

from collections.abc import Callable, Iterable
from typing import TypeVar, Any

import polars as pl

from ..funcs import dc, fn
from .._protocols import CheckFunc, ProcessFunc, TransformFunc
K = TypeVar("K")
K1 = TypeVar("K1")
V = TypeVar("V")
V1 = TypeVar("V1")

cdef class Struct:
    _value: dict[Any, Any]
    _pipeline: list[Callable[[dict[Any, Any]], Any]]

    def __init__(self, _value: dict[Any, Any], _pipeline: list[Callable[[dict[Any, Any]], Any]] | None = None):
        self._value = _value
        self._pipeline = _pipeline if _pipeline is not None else []

    def __repr__(self):
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    cdef _do(self, f: ProcessFunc[dict[Any, Any]]):
        self._pipeline.append(f)
        return self

    cdef _into(self, f: TransformFunc[dict[Any, Any], dict[Any, Any]]):
        return self.__class__(
            _value=self._value,
            _pipeline=[fn.compose(*self._pipeline, f)],
        )

    cpdef clone(self):
        return self.__class__(fn.clone(self._value), fn.clone(self._pipeline))

    cpdef unwrap(self):
        if not self._pipeline:
            return self._value
        return fn.pipe(self._value, *self._pipeline)

    cpdef map_keys(self, f: TransformFunc[K, K1]):
        return self._into(f=dc.map_keys(f))

    cpdef map_values(self, f: TransformFunc[V, V1]):
        return self._into(f=dc.map_values(f=f))

    cpdef select(self, predicate: CheckFunc[K]):
        return self._do(f=dc.filter_keys(predicate=predicate))

    cpdef filter(self, predicate: CheckFunc[V]):
        return self._do(f=dc.filter_values(predicate=predicate))

    cpdef filter_on_key(self, key: Any, predicate: CheckFunc[V]):
        return self._do(dc.filter_on_key(key=key, predicate=predicate))

    cpdef with_key(self, key: Any, value: Any):
        return self._do(f=dc.with_key(key=key, value=value))

    cpdef with_nested_key(self, keys: Iterable[K] | K, value: Any):
        return self._do(f=dc.with_nested_key(keys=keys, value=value))

    cpdef flatten_keys(self):
        return self._into(f=dc.flatten_keys())

    cpdef to_obj(self, obj: Callable[[dict[Any, Any]], Any]):
        return obj(self.unwrap())

    cpdef to_frame(self):
        return pl.DataFrame(self.unwrap())

    def update_in(self, *keys: Any, f: ProcessFunc[V]):
        return self._do(f=dc.update_in(*keys, f=f))

    def merge(self, *others: dict[Any, Any]):
        return self._do(f=dc.merge(others=others))

    def merge_with(self, f: Callable[[Any], Any], *others: dict[Any, Any]):
        return self._do(f=dc.merge_with(f, *others))

    def drop(self, *keys: Any):
        return self._do(f=dc.drop(keys=keys))
