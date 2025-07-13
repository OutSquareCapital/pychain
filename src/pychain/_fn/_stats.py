import statistics as stats
from functools import partial
from collections.abc import Iterable
from typing import Literal, Any


def quantiles(
    n: int, method: Literal["inclusive", "exclusive"] = "exclusive"
) -> partial[Iterable[Any]]:
    return partial(stats.quantiles, n=n, method=method)
