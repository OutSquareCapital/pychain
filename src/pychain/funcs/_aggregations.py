import statistics as stats
from collections.abc import Callable, Iterable
from functools import partial
from typing import Any

import cytoolz.itertoolz as itz
import numpy as np
import polars as pl

from .._protocols import TransformFunc
from ._functions import partial_map

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

frequencies = itz.frequencies


def group_by[K, V](on: TransformFunc[V, K]) -> partial[dict[K, list[V]]]:
    return partial(itz.groupby, on)


def reduce_by[K, V](
    key: TransformFunc[V, K], binop: Callable[[V, V], V]
) -> partial[dict[K, V]]:
    return partial(itz.reduceby, key=key, binop=binop)


def to_records(keys: list[str]):
    return partial_map(lambda row: dict(zip(keys, row)))  # type: ignore


def at_index(index: int) -> partial[Any]:
    return partial(itz.nth, index)


def agg(on: Callable[[Iterable[Any]], Any]):
    return partial(on)


def to_obj(obj: Callable[[Iterable[Any]], Any]):
    return obj


def to_list():
    return list


def to_set():
    return set


def to_array():
    return np.array


def to_series():
    return pl.Series
