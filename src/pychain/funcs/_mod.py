# distutils: language=c++
import operator as op
import statistics as stats
from collections.abc import Callable, Iterable, Iterator
from functools import partial
from typing import Any, Literal, TypeVar, ParamSpec
import cytoolz.itertoolz as itz
import cytoolz.functoolz as ftz

from .._protocols import ThreadFunc, TransformFunc
from copy import deepcopy

T = TypeVar("T")
V = TypeVar("V")
V1 = TypeVar("V1")
T1 = TypeVar("T1")
K = TypeVar("K")
K1 = TypeVar("K1")
P = ParamSpec("P")

first = itz.first
second = itz.second
last = itz.last
length = itz.count
mean = stats.mean
median = stats.median
mode = stats.mode
stdev = stats.stdev
variance = stats.variance
pvariance = stats.pvariance
median_low = stats.median_low
median_high = stats.median_high
median_grouped = stats.median_grouped

is_all = all
is_any = any
is_distinct = itz.isdistinct

is_all = all
is_any = any

is_iterable = itz.isiterable
compose = ftz.compose_left
pipe = ftz.pipe
clone = deepcopy

def _runner(
    p1: Callable[P, bool], p2: Callable[P, bool], *args: P.args, **kwargs: P.kwargs
) :
    return op.and_(p1(*args, **kwargs), p2(*args, **kwargs))

def _binder(p1: Callable[P, bool], p2: Callable[P, bool]) :
    return partial(_runner, p1, p2)

def _thread_first(val: T, fns: Iterable[ThreadFunc[T]]) :
    return ftz.thread_first(val, *fns)


def _thread_last(val: T, fns: Iterable[ThreadFunc[T]]) :
    return ftz.thread_last(val, *fns)

def compose_on_iter(
    fns: Iterable[TransformFunc[V, V1]],
) -> partial[Iterator[V1]]:
    return partial(map, ftz.compose_left(*fns))

def and_(
    p1: Callable[P, bool],
) :
    return partial(_binder, p1)

#-----------------------

def from_func(value: T, f: Callable[[T], T1]):
    return itz.iterate(f, value)

def from_range(start: int, stop: int, step: int = 1):
    return range(start, stop, step)

def iter_to_dict(value: Iterable[V]):
    return dict(enumerate(value))

def thread_first(fns: Iterable[ThreadFunc[T]]) :
    return partial(_thread_first, fns=fns)


def thread_last(fns: Iterable[ThreadFunc[T]]) :
    return partial(_thread_last, fns=fns)

def at_index(index: int) :
    return partial(itz.nth, index)


def agg(on: Callable[[Iterable[Any]], Any]):
    return partial(on)



class Sign:
    _master_func: Callable[[Any], Any]
    _internal_funcs: tuple[Callable[[Any], Any], ...]

    def __init__(
        self, master_func: Callable[[Any], Any], *internal_funcs: Callable[[Any], Any]
    ) :
        self._master_func: Callable[[Any], Any] = master_func
        self._internal_funcs: tuple[Callable[[Any], Any], ...] = internal_funcs

    def __call__(self, *args: Any, **kwargs: Any) :
        results: list[Any] = [f(*args, **kwargs) for f in self._internal_funcs]

        return self._master_func(*results)

    def __class_getitem__(cls, key: tuple[type, ...]) :
        return cls

def quantiles(
    n: int, method: Literal["inclusive", "exclusive"] = "exclusive"
) :
    return partial(stats.quantiles, n=n, method=method)
