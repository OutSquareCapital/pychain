import functools
import statistics
from collections.abc import Callable, Iterable
from typing import Literal

import cytoolz as cz
import more_itertools as mit

from .._core import CommonBase
from .._protocols import SupportsRichComparison


class IterAgg[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """
        Apply a function of two arguments cumulatively to the items of an iterable, from left to right.
        This effectively reduces the iterable to a single value.
        If initial is present, it is placed before the items of the iterable in the calculation.
        It then serves as a default when the iterable is empty.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).reduce(lambda a, b: a + b)
            6
        """
        return functools.reduce(func, self._data)

    def is_distinct(self) -> bool:
        """
        Return True if all items are distinct.

            >>> from pychain import Iter
            >>> Iter([1, 2]).is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """
        Return True if all items are truthy.

            >>> from pychain import Iter
            >>> Iter([1, True]).all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """
        Return True if any item is truthy.

            >>> from pychain import Iter
            >>> Iter([0, 1]).any()
            True
        """
        return any(self._data)

    def first(self) -> T:
        """
        Return the first element.

            >>> from pychain import Iter
            >>> Iter([9]).first()
            9
        """
        return cz.itertoolz.first(self._data)

    def second(self) -> T:
        """
        Return the second element.

            >>> from pychain import Iter
            >>> Iter([9, 8]).second()
            8
        """
        return cz.itertoolz.second(self._data)

    def last(self) -> T:
        """
        Return the last element.

            >>> from pychain import Iter
            >>> Iter([7, 8, 9]).last()
            9
        """
        return cz.itertoolz.last(self._data)

    def length(self) -> int:
        """
        Return the length of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2]).length()
            2
        """
        return cz.itertoolz.count(self._data)

    def item(self, index: int) -> T:
        """
        Return item at index.

            >>> from pychain import Iter
            >>> Iter([10, 20]).item(1)
            20
        """
        return cz.itertoolz.nth(index, self._data)

    def all_equal[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Return True if all items are equal.

            >>> from pychain import Iter
            >>> Iter([1, 1, 1]).all_equal()
            True
        """
        return mit.all_equal(self._data, key=key)

    def all_unique[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Return True if all items are unique.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).all_unique()
            True
        """
        return mit.all_unique(self._data, key=key)

    def argmax[U](self, key: Callable[[T], U] | None = None) -> int:
        """
        Return the index of the maximum value in the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).argmax()
            1
        """
        return mit.argmax(self._data, key=key)

    def argmin[U](self, key: Callable[[T], U] | None = None) -> int:
        """
        Return the index of the minimum value in the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).argmin()
            0
        """
        return mit.argmin(self._data, key=key)

    def is_sorted[U](
        self,
        key: Callable[[T], U] | None = None,
        reverse: bool = False,
        strict: bool = True,
    ) -> bool:
        """
        Return True if the sequence is sorted.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).is_sorted()
            True
        """
        return mit.is_sorted(self._data, key=key, reverse=reverse, strict=strict)

    def sum[U: int | float](self: CommonBase[Iterable[U]]) -> U | Literal[0]:
        """
        Return the sum of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).sum()
            6
        """
        return sum(self._data)

    def min[U: int | float](
        self: CommonBase[Iterable[U]],
        key: Callable[[U], SupportsRichComparison[U]] | None = None,
    ) -> U:
        """
        Return the minimum value of the sequence.

            >>> from pychain import Iter
            >>> Iter([3, 1, 2]).min()
            1
        """
        return min(self._data, key=key)

    def max[U: int | float](
        self: CommonBase[Iterable[U]],
        key: Callable[[U], SupportsRichComparison[U]] | None = None,
    ) -> U:
        """
        Return the maximum value of the sequence.

            >>> from pychain import Iter
            >>> Iter([3, 1, 2]).max()
            3
        """
        return max(self._data, key=key)

    def mean[U: int | float](self: CommonBase[Iterable[U]]) -> float:
        """
        Return the mean of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).mean()
            2
        """
        return statistics.mean(self._data)

    def median[U: int | float](self: CommonBase[Iterable[U]]) -> float:
        """
        Return the median of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).median()
            2
        """
        return statistics.median(self._data)

    def mode[U: int | float](self: CommonBase[Iterable[U]]) -> U | Literal[0]:
        """
        Return the mode of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2, 2, 3]).mode()
            2
        """
        return statistics.mode(self._data)

    def stdev[U: int | float](
        self: "CommonBase[Iterable[U]]",
    ) -> float | Literal[0]:
        """
        Return the standard deviation of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).stdev()
            1.0
        """
        return statistics.stdev(self._data)

    def variance[U: int | float](
        self: "CommonBase[Iterable[U]]",
    ) -> float | Literal[0]:
        """
        Return the variance of the sequence.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 7, 8]).variance()
            9.7
        """
        return statistics.variance(self._data)
