# distutils: language=c++

from collections.abc import Callable, Container
import statistics as stats
from typing import Any, Literal
from .._fn import (
    bo,
    op,
    fn,
    st,
)

cdef class ChainableOp:
    _pipeline: Callable[[Any], Any]
    def __init__(self, pipeline: Callable[[Any], Any]):
        self._pipeline = pipeline

    def __call__(self, value: Any) -> Any:
        return self._pipeline(value)

    def _chain(self, new_op: Callable[[Any], Any]):
        def composed(x: Any):
            return new_op(self._pipeline(x))

        return self.__class__(pipeline=composed)

    def attr(self, name: str):
        return self._chain(fn.attr(name))

    def item(self, key: Any):
        return self._chain(fn.item(key))

    def method(self, name: str, *args: Any, **kwargs: Any):
        return self._chain(fn.method(name, *args, **kwargs))

    def add(self, value: Any):
        return self._chain(op.add(value))

    def sub(self, value: Any):
        return self._chain(op.sub(value))

    def mul(self, value: Any):
        return self._chain(op.mul(value))

    def truediv(self, value: Any):
        return self._chain(op.truediv(value))

    def floordiv(self, value: Any):
        return self._chain(op.floordiv(value))

    def sub_r(self, value: Any):
        return self._chain(op.sub_r(value))

    def truediv_r(self, value: Any):
        return self._chain(op.truediv_r(value))

    def floordiv_r(self, value: Any):
        return self._chain(op.floordiv_r(value))

    def mod(self, value: Any):
        return self._chain(op.mod(value))

    def pow(self, value: Any):
        return self._chain(op.pow(value))

    def neg(self):
        return self._chain(op.neg)

    def is_true(self):
        return self._chain(bo.is_true)

    def is_none(self):
        return self._chain(bo.is_none())

    def is_not_none(self):
        return self._chain(bo.is_not_none())

    def is_in(self, values: Container[Any]):
        return self._chain(bo.is_in(values))

    def is_not_in(self, values: Container[Any]):
        return self._chain(bo.is_not_in(values))

    def is_distinct(self):
        return self._chain(bo.is_distinct)

    def is_iterable(self):
        return self._chain(bo.is_iterable)

    def is_all(self):
        return self._chain(bo.is_all)

    def is_any(self):
        return self._chain(bo.is_any)

    def eq(self, value: Any):
        return self._chain(bo.eq(value))

    def ne(self, value: Any):
        return self._chain(bo.ne(value))

    def gt(self, value: Any):
        return self._chain(bo.gt(value))

    def ge(self, value: Any):
        return self._chain(bo.ge(value))

    def lt(self, value: Any):
        return self._chain(bo.lt(value))

    def le(self, value: Any):
        return self._chain(bo.le(value))

    def mean(self):
        return self._chain(stats.mean)

    def median(self):
        return self._chain(stats.median)

    def mode(self):
        return self._chain(stats.mode)

    def stdev(self):
        return self._chain(stats.stdev)

    def variance(self):
        return self._chain(stats.variance)
    
    def pvariance(self):
        return self._chain(stats.pvariance)

    def median_low(self):
        return self._chain(stats.median_low)

    def median_high(self):
        return self._chain(stats.median_high)

    def median_grouped(self):
        return self._chain(stats.median_grouped)

    def quantiles(self, n: int, method: Literal["inclusive", "exclusive"] = "exclusive"):
        return self._chain(st.quantiles(n, method=method))

    def min(self):
        return self._chain(min)

    def max(self):
        return self._chain(max)

    def sum(self):
        return self._chain(sum)


cdef class OpConstructor:
    def __call__(self, name: str) -> ChainableOp:
        return ChainableOp(fn.attr(name))

    def item(self, key: Any):
        return ChainableOp(fn.item(key))

    def method(self, name: str, *args: Any, **kwargs: Any):
        return ChainableOp(fn.method(name, *args, **kwargs))

    def add(self, value: Any):
        return ChainableOp(op.add(value))

    def sub(self, value: Any):
        return ChainableOp(op.sub(value))

    def mul(self, value: Any):
        return ChainableOp(op.mul(value))

    def truediv(self, value: Any):
        return ChainableOp(op.truediv(value))

    def floordiv(self, value: Any):
        return ChainableOp(op.floordiv(value))

    def sub_r(self, value: Any):
        return ChainableOp(op.sub_r(value))

    def truediv_r(self, value: Any):
        return ChainableOp(op.truediv_r(value))

    def floordiv_r(self, value: Any):
        return ChainableOp(op.floordiv_r(value))

    def mod(self, value: Any):
        return ChainableOp(op.mod(value))

    def pow(self, value: Any):
        return ChainableOp(op.pow(value))

    def neg(self):
        return ChainableOp(op.neg)

    def is_true(self):
        return ChainableOp(bo.is_true)

    def is_none(self):
        return ChainableOp(bo.is_none())

    def is_not_none(self):
        return ChainableOp(bo.is_not_none())

    def is_in(self, values: Container[Any]):
        return ChainableOp(bo.is_in(values))

    def is_not_in(self, values: Container[Any]):
        return ChainableOp(bo.is_not_in(values))

    def is_distinct(self):
        return ChainableOp(bo.is_distinct)

    def is_iterable(self):
        return ChainableOp(bo.is_iterable)

    def is_all(self):
        return ChainableOp(bo.is_all)

    def is_any(self):
        return ChainableOp(bo.is_any)

    def eq(self, value: Any):
        return ChainableOp(bo.eq(value))

    def ne(self, value: Any):
        return ChainableOp(bo.ne(value))

    def gt(self, value: Any):
        return ChainableOp(bo.gt(value))

    def ge(self, value: Any):
        return ChainableOp(bo.ge(value))

    def lt(self, value: Any):
        return ChainableOp(bo.lt(value))

    def le(self, value: Any):
        return ChainableOp(bo.le(value))

    def mean(self):
        return ChainableOp(stats.mean)

    def median(self):
        return ChainableOp(stats.median)

    def mode(self):
        return ChainableOp(stats.mode)

    def stdev(self):
        return ChainableOp(stats.stdev)

    def variance(self):
        return ChainableOp(stats.variance)
    
    def pvariance(self):
        return ChainableOp(stats.pvariance)

    def median_low(self):
        return ChainableOp(stats.median_low)

    def median_high(self):
        return ChainableOp(stats.median_high)

    def median_grouped(self):
        return ChainableOp(stats.median_grouped)

    def quantiles(self, n: int, method: Literal["inclusive", "exclusive"] = "exclusive"):
        return ChainableOp(st.quantiles(n, method=method))

    def min(self):
        return ChainableOp(min)

    def max(self):
        return ChainableOp(max)

    def sum(self):
        return ChainableOp(sum)
