# distutils: language=c++

from collections.abc import Callable, Container
from typing import Any, TypeVar
from ..funcs import (
    bo,
    op,
    fn
)
T = TypeVar("T")

cdef class OpConstructor:
    def __call__(self, *dtype: type):
        return Op(fn.identity)

    cpdef attr(self, name: str, dtype: type):
        return Op(fn.attr(name))

    cpdef item(self, key: Any, dtype: type):
        return Op(fn.item(key))

cdef class Op:
    _pipeline: Callable[[Any], Any]

    def __init__(self, pipeline: Callable[[Any], Any]):
        self._pipeline = pipeline

    def __call__(self, value: Any):
        return self._pipeline(value)

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    def __class_getitem__(cls, key: tuple[type, ...]) -> type:
        return cls
    def _do(self, f: Callable[[Any], Any]):
        def _new_pipeline(value: Any):
            return f(self._pipeline(value))
        return self.__class__(pipeline=_new_pipeline)

    def and_(self, *others: Callable[[Any], bool]):
        def _new_pipeline(value: Any) -> bool:
            all_checks = (self,) + others
            return all(check(value) for check in all_checks)
        return self.__class__(pipeline=_new_pipeline)

    cpdef hint(self, dtype: type):
        return self

    cpdef into(self, obj: Callable[[Any], Any]):
        return self._do(obj)

    cpdef add(self, value: Any):
        return self._do(op.add(value))

    cpdef sub(self, value: Any):
        return self._do(op.sub(value))

    cpdef mul(self, value: Any):
        return self._do(op.mul(value))

    cpdef truediv(self, value: Any):
        return self._do(op.truediv(value))

    cpdef floordiv(self, value: Any):
        return self._do(op.floordiv(value))

    cpdef sub_r(self, value: Any):
        return self._do(op.sub_r(value))

    cpdef truediv_r(self, value: Any):
        return self._do(op.truediv_r(value))

    cpdef floordiv_r(self, value: Any):
        return self._do(op.floordiv_r(value))

    cpdef mod(self, value: Any):
        return self._do(op.mod(value))

    cpdef pow(self, value: Any):
        return self._do(op.pow(value))

    cpdef neg(self):
        return self._do(op.neg)

    cpdef round_to(self, ndigits: int):
        return self._do(op.round_to(ndigits))

    cpdef is_true(self):
        return self._do(bo.is_true)

    cpdef is_none(self):
        return self._do(bo.is_none())

    cpdef is_not_none(self):
        return self._do(bo.is_not_none())

    cpdef is_in(self, values: Container[Any]):
        return self._do(bo.is_in(values))

    cpdef is_not_in(self, values: Container[Any]):
        return self._do(bo.is_not_in(values))

    cpdef is_iterable(self):
        return self._do(bo.is_iterable)

    cpdef eq(self, value: Any):
        return self._do(bo.eq(value))

    cpdef ne(self, value: Any):
        return self._do(bo.ne(value))

    cpdef gt(self, value: Any):
        return self._do(bo.gt(value))

    cpdef ge(self, value: Any):
        return self._do(bo.ge(value))

    cpdef lt(self, value: Any):
        return self._do(bo.lt(value))

    cpdef le(self, value: Any):
        return self._do(bo.le(value))
