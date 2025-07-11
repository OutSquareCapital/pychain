import statistics as stats
from functools import partial
from typing import Literal

def quantiles(n: int, method: Literal["inclusive", "exclusive"]):
    """
    Calculate quantiles of the input data.

    Example:
        >>> ChainableOp().quantiles(4, "inclusive")([1, 2, 3, 4, 5])
        [2.0, 3.0, 4.0]

        >>> ChainableOp().quantiles(4, "exclusive")([1, 2, 3, 4, 5])
        [1.5, 3.0, 4.5]
    """
    return partial(stats.quantiles, n=n, method=method)
