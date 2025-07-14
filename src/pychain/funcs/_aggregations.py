import statistics as stats
from functools import partial
from typing import Any

import cytoolz.itertoolz as itz

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


def at_index(index: int) -> partial[Any]:
    return partial(itz.nth, index)
