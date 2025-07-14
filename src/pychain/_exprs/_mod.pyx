# distutils: language=c++

from collections.abc import Callable, Container
import statistics as stats
from typing import Any, Literal
from ..funcs import (
    bo,
    op,
    fn,
    st,
)

cdef class ChainableOp:
    _pipeline: Callable[[Any], Any]

    def __init__(self):
        self._pipeline = fn.identity

    def __call__(self, value: Any):
        return self._pipeline(value)

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:[\n{self._pipeline}\n])"

    cdef _do(self, f: Callable[[Any], Any]):
        self._pipeline = fn.compose(self._pipeline, f)
        return self

    cpdef attr(self, name: str):
        return self._do(fn.attr(name))

    cpdef item(self, key: Any):
        return self._do(fn.item(key))
    
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

    cpdef is_distinct(self):
        return self._do(bo.is_distinct)

    cpdef is_iterable(self):
        return self._do(bo.is_iterable)

    cpdef is_all(self):
        return self._do(bo.is_all)

    cpdef is_any(self):
        return self._do(bo.is_any)

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

    cpdef mean(self):
        return self._do(stats.mean)

    cpdef median(self):
        return self._do(stats.median)

    cpdef mode(self):
        return self._do(stats.mode)

    cpdef stdev(self):
        return self._do(stats.stdev)

    cpdef variance(self):
        return self._do(stats.variance)

    cpdef pvariance(self):
        return self._do(stats.pvariance)

    cpdef median_low(self):
        return self._do(stats.median_low)

    cpdef median_high(self):
        return self._do(stats.median_high)

    cpdef median_grouped(self):
        return self._do(stats.median_grouped)

    cpdef quantiles(self, n: int, method: Literal["inclusive", "exclusive"] = "exclusive"):
        return self._do(st.quantiles(n, method=method))

    cpdef min(self):
        return self._do(min)

    cpdef max(self):
        return self._do(max)

    cpdef sum(self):
        return self._do(sum)

cdef class OpConstructor:
    def __call__(self, *dtype: type):
        return ChainableOp()
