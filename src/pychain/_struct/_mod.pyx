# distutils: language=c++

from collections.abc import Callable, Iterable
from typing import TypeVar, Any

from ..funcs import dc
from ..funcs._functions import identity
from .._protocols import CheckFunc, ProcessFunc, TransformFunc
K = TypeVar("K")
K1 = TypeVar("K1")
V = TypeVar("V")
V1 = TypeVar("V1")

cdef class StructConstructor:
    def __call__(self, ktype: type, vtype: type):
        return Struct(identity)

cdef class Struct:
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

    cpdef to_obj(self, obj: Callable[[dict[Any, Any]], Any]):
        return self._do(obj)

    cpdef map_keys(self, f: TransformFunc[K, K1]):
        return self._do(f=dc.map_keys(f))

    cpdef map_values(self, f: TransformFunc[V, V1]):
        return self._do(f=dc.map_values(f=f))

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
        return self._do(f=dc.flatten_keys())

    cpdef update_in(self, keys: Iterable[Any], f: ProcessFunc[V]):
        return self._do(f=dc.update_in(keys=keys, f=f))

    cpdef merge(self, others: Iterable[dict[Any, Any]]):
        return self._do(f=dc.merge(others=others))

    cpdef merge_with(self, f: Callable[[Any], Any], others: Iterable[dict[Any, Any]]):
        return self._do(f=dc.merge_with(f, *others))

    cpdef drop(self, keys: Iterable[Any]):
        return self._do(f=dc.drop(keys=keys))
