import statistics
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import reduce
from typing import Concatenate, Literal

import cytoolz as cz


@dataclass(slots=True)
class Aggregator[T]:
    """Namespace for aggregation functions."""

    _data: Iterable[T]

    def __call__[**P](
        self,
        f: Callable[Concatenate[Iterable[T], P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Apply aggregator f to the whole Iterable and return result.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2]).agg(sum)
            3
        """
        return f(self._data, *args, **kwargs)

    def sum[U: int | float](self: "Aggregator[U]") -> U | Literal[0]:
        """Return the sum of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).agg.sum()
            6
        """
        return sum(self._data)

    def min[U: int | float](self: "Aggregator[U]") -> U:
        """Return the minimum value of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([3, 1, 2]).agg.min()
            1
        """
        return min(self._data)

    def max[U: int | float](self: "Aggregator[U]") -> U:
        """Return the maximum value of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([3, 1, 2]).agg.max()
            3
        """
        return max(self._data)

    def mean[U: int | float](self: "Aggregator[U]") -> float:
        """Return the mean of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).agg.mean()
            2
        """
        return statistics.mean(self._data)

    def median[U: int | float](self: "Aggregator[U]") -> float:
        """Return the median of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).agg.median()
            2
        """
        return statistics.median(self._data)

    def mode[U: int | float](self: "Aggregator[U]") -> U | Literal[0]:
        """Return the mode of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 2, 3]).agg.mode()
            2
        """
        return statistics.mode(self._data)

    def stdev[U: int | float](self: "Aggregator[U]") -> float | Literal[0]:
        """Return the standard deviation of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).agg.stdev()
            1.0
        """
        return statistics.stdev(self._data)

    def variance[U: int | float](self: "Aggregator[U]") -> float | Literal[0]:
        """Return the variance of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 7, 8]).agg.variance()
            9.7
        """
        return statistics.variance(self._data)

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce the sequence using func.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).agg.reduce(lambda a, b: a + b)
            6
        """
        return reduce(func, self._data)

    def is_distinct(self) -> bool:
        """Return True if all items are distinct.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2]).agg.is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """Return True if all items are truthy.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, True]).agg.all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """Return True if any item is truthy.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([0, 1]).agg.any()
            True
        """
        return any(self._data)

    def first(self) -> T:
        """Return the first element.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([9]).agg.first()
            9
        """
        return cz.itertoolz.first(self._data)

    def second(self) -> T:
        """Return the second element.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([9, 8]).agg.second()
            8
        """
        return cz.itertoolz.second(self._data)

    def last(self) -> T:
        """Return the last element.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([7, 8, 9]).agg.last()
            9
        """
        return cz.itertoolz.last(self._data)

    def length(self) -> int:
        """Return the length of the sequence.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2]).agg.length()
            2
        """
        return cz.itertoolz.count(self._data)

    def at_index(self, index: int) -> T:
        """Return item at index.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([10, 20]).agg.at_index(1)
            20
        """
        return cz.itertoolz.nth(index, self._data)
