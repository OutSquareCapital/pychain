# distutils: language=c++

from collections.abc import Callable, Container
import statistics as stats
from typing import Any
from .. import _fn

cdef identity(x: Any):
    return x

cdef class ChainableOp:
    _pipeline: Callable[[Any], Any]
    def __init__(self, pipeline: Callable[[Any], Any] | None = None):
        if pipeline is None:
            self._pipeline = identity
        else:
            self._pipeline = pipeline

    def __call__(self, value: Any) -> Any:
        return self._pipeline(value)

    def _chain(self, new_op: Callable[[Any], Any]):
        def composed(x: Any):
            return new_op(self._pipeline(x))

        return self.__class__(pipeline=composed)
    
    def attr(self, *names: str):
        return self._chain(_fn.attr(*names))

    def item(self, *keys: Any):
        return self._chain(_fn.item(*keys))

    def method(self, name: str, *args: Any, **kwargs: Any):
        return self._chain(_fn.method(name, *args, **kwargs))

    def add(self, value: Any):
        return self._chain(_fn.add(value))

    def sub(self, value: Any):
        return self._chain(_fn.sub(value))

    def mul(self, value: Any):
        return self._chain(_fn.mul(value))

    def truediv(self, value: Any):
        return self._chain(_fn.truediv(value))

    def floordiv(self, value: Any):
        return self._chain(_fn.floordiv(value))

    def sub_r(self, value: Any):
        return self._chain(_fn.sub_r(value))

    def truediv_r(self, value: Any):
        return self._chain(_fn.truediv_r(value))

    def floordiv_r(self, value: Any):
        return self._chain(_fn.floordiv_r(value))

    def mod(self, value: Any):
        return self._chain(_fn.mod(value))

    def pow(self, value: Any):
        return self._chain(_fn.pow(value))

    def neg(self):
        return self._chain(_fn.neg)

    def is_true(self):
        return self._chain(_fn.is_true)

    def is_none(self):
        return self._chain(_fn.is_none())

    def is_not_none(self):
        return self._chain(_fn.is_not_none())

    def is_in(self, values: Container[Any]):
        return self._chain(_fn.is_in(values))

    def is_not_in(self, values: Container[Any]):
        return self._chain(_fn.is_not_in(values))

    def is_distinct(self):
        return self._chain(_fn.is_distinct)

    def is_iterable(self):
        return self._chain(_fn.is_iterable)

    def is_all(self):
        return self._chain(_fn.is_all)

    def is_any(self):
        return self._chain(_fn.is_any)

    def eq(self, value: Any):
        return self._chain(_fn.eq(value))

    def ne(self, value: Any):
        return self._chain(_fn.ne(value))

    def gt(self, value: Any):
        return self._chain(_fn.gt(value))

    def ge(self, value: Any):
        return self._chain(_fn.ge(value))

    def lt(self, value: Any):
        return self._chain(_fn.lt(value))

    def le(self, value: Any):
        return self._chain(_fn.le(value))

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

    def quantiles(self, *args: Any):
        return self._chain(_fn.quantiles(*args))

    def min(self):
        return self._chain(min)

    def max(self):
        return self._chain(max)

    def sum(self):
        return self._chain(sum)


cdef class OpConstructor:
    def __call__(self, name: str | None = None) -> ChainableOp:
        if name is None:
            return ChainableOp()
        return ChainableOp().attr(name)

    def __getattr__(self, name: str) -> ChainableOp:
        return self(name)
