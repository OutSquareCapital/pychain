from __future__ import annotations

import functools
import statistics
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper, SupportsRichComparison

if TYPE_CHECKING:
    from .._expressions import Expr
    from .._iter import Iter


class BaseAgg[T](IterWrapper[T]):
    @overload
    def reduce(self: Iter[T], func: Callable[[T, T], T]) -> T: ...
    @overload
    def reduce(self: Expr, func: Callable[[Any, Any], Any]) -> Expr: ...
    def reduce(self, func: Callable[[T, T], T]):
        """
        Apply a function of two arguments cumulatively to the items of an iterable, from left to right.

        This effectively reduces the iterable to a single value.

        If initial is present, it is placed before the items of the iterable in the calculation.

        It then serves as a default when the iterable is empty.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).reduce(lambda a, b: a + b)
            6
        """
        return self.into(functools.partial(functools.reduce, func))

    @overload
    def combination_index(self: Iter[T], r: Iterable[T]) -> int: ...
    @overload
    def combination_index(self: Expr, r: Iterable[Any]) -> Expr: ...
    def combination_index(self, r: Iterable[T]):
        """
        Equivalent to list(combinations(iterable, r)).index(element)

        The subsequences of iterable that are of length r can be ordered lexicographically.

        combination_index computes the index of the first element, without computing the previous combinations.

        >>> from pychain import Iter
        >>> Iter("abcdefg").combination_index("adf")
        10

        ValueError will be raised if the given element isn't one of the combinations of iterable.
        """
        return self.into(functools.partial(mit.combination_index, r))

    @overload
    def first(self: Iter[T]) -> T: ...
    @overload
    def first(self: Expr) -> Expr: ...

    def first(self):
        """
        Return the first element.

            >>> from pychain import Iter
            >>> Iter([9]).first()
            9
        """
        return self.into(cz.itertoolz.first)

    @overload
    def second(self: Iter[T]) -> T: ...
    @overload
    def second(self: Expr) -> Expr: ...
    def second(self):
        """
        Return the second element.

            >>> from pychain import Iter
            >>> Iter([9, 8]).second()
            8
        """
        return self.into(cz.itertoolz.second)

    @overload
    def last(self: Iter[T]) -> T: ...
    @overload
    def last(self: Expr) -> Expr: ...
    def last(self):
        """
        Return the last element.

            >>> from pychain import Iter
            >>> Iter([7, 8, 9]).last()
            9
        """
        return self.into(cz.itertoolz.last)

    @overload
    def length(self: Iter[T]) -> int: ...
    @overload
    def length(self: Expr) -> Expr: ...
    def length(self):
        """
        Return the length of the sequence.
        Like the builtin len but works on lazy sequences.

            >>> from pychain import Iter
            >>> Iter([1, 2]).length()
            2
        """
        return self.into(cz.itertoolz.count)

    @overload
    def item(self: Iter[T], index: int) -> T: ...
    @overload
    def item(self: Expr, index: int) -> Expr: ...
    def item(self, index: int):
        """
        Return item at index.

        >>> from pychain import Iter
        >>> Iter([10, 20]).item(1)
        20
        """
        return self.into(functools.partial(cz.itertoolz.nth, index))

    @overload
    def argmax[U](self: Iter[T], key: Callable[[T], U] | None = None) -> int: ...
    @overload
    def argmax[U](self: Expr, key: Callable[[T], U] | None = None) -> Expr: ...
    def argmax[U](self, key: Callable[[T], U] | None = None):
        """
        Index of the first occurrence of a maximum value in an iterable.

        >>> from pychain import Iter
        >>> Iter("abcdefghabcd").argmax()
        7
        >>> Iter([0, 1, 2, 3, 3, 2, 1, 0]).argmax()
        3

        For example, identify the best machine learning model:

        >>> models = Iter(["svm", "random forest", "knn", "naïve bayes"])
        >>> accuracy = Iter([68, 61, 84, 72])
        >>> # Most accurate model
        >>> models.item(accuracy.argmax())
        'knn'

        >>> # Best accuracy
        >>> accuracy.max()
        84
        """
        return self.into(mit.argmax, key=key)

    @overload
    def argmin[U](self: Iter[T], key: Callable[[T], U] | None = None) -> int: ...
    @overload
    def argmin[U](self: Expr, key: Callable[[T], U] | None = None) -> Expr: ...
    def argmin[U](self, key: Callable[[T], U] | None = None):
        """
        Index of the first occurrence of a minimum value in an iterable.

        >>> from pychain import Iter
        >>> Iter("efghabcdijkl").argmin()
        4
        >>> Iter([3, 2, 1, 0, 4, 2, 1, 0]).argmin()
        3

        For example, look up a label corresponding to the position of a value that minimizes a cost function:

        >>> def cost(x):
        ...     "Days for a wound to heal given a subject's age."
        ...     return x**2 - 20 * x + 150
        >>> labels = Iter(["homer", "marge", "bart", "lisa", "maggie"])
        >>> ages = Iter([35, 30, 10, 9, 1])

        >>> # Fastest healing family member
        >>> labels.item(ages.argmin(key=cost))
        'bart'

        >>> # Age with fastest healing
        >>> ages.min(key=cost)
        10
        """
        return self.into(mit.argmin, key=key)

    @overload
    def sum(self: Iter[int]) -> int: ...
    @overload
    def sum(self: Iter[float]) -> float: ...
    @overload
    def sum(self: Expr) -> Expr: ...

    def sum(self):
        """
        Return the sum of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).sum()
        6
        """
        return self.into(sum)

    @overload
    def min[U: int | float](
        self: Iter[U], key: Callable[[U], SupportsRichComparison[U]] | None = None
    ) -> U: ...
    @overload
    def min(
        self: Expr, key: Callable[[Any], SupportsRichComparison[Any]] | None = None
    ) -> Expr: ...
    def min(
        self,
        key: Callable[[Any], SupportsRichComparison[Any]] | None = None,
    ):
        """
        Return the minimum value of the sequence.

        >>> from pychain import Iter
        >>> Iter([3, 1, 2]).min()
        1
        """
        return self.into(min, key=key)

    @overload
    def max[U: int | float](
        self: Iter[U], key: Callable[[U], SupportsRichComparison[U]] | None = None
    ) -> U: ...
    @overload
    def max(
        self: Expr, key: Callable[[Any], SupportsRichComparison[Any]] | None = None
    ) -> Expr: ...

    def max(
        self,
        key: Callable[[Any], SupportsRichComparison[Any]] | None = None,
    ):
        """
        Return the maximum value of the sequence.

        >>> from pychain import Iter
        >>> Iter([3, 1, 2]).max()
        3
        """
        return self.into(max, key=key)

    @overload
    def mean[U: int | float](self: Iter[U]) -> float: ...
    @overload
    def mean(self: Expr) -> Expr: ...
    def mean(self):
        """
        Return the mean of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).mean()
        2
        """
        return self.into(statistics.mean)

    @overload
    def median[U: int | float](self: Iter[U]) -> float: ...
    @overload
    def median(self: Expr) -> Expr: ...
    def median(self):
        """
        Return the median of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 3, 2]).median()
        2
        """
        return self.into(statistics.median)

    @overload
    def mode[U: int | float](self: Iter[U]) -> U: ...
    @overload
    def mode(self: Expr) -> Expr: ...
    def mode(self):
        """
        Return the mode of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 2, 3]).mode()
        2
        """
        return self.into(statistics.mode)

    @overload
    def stdev[U: int | float](
        self: Iter[U],
    ) -> float: ...
    @overload
    def stdev(self: Expr) -> Expr: ...
    def stdev(self):
        """
        Return the standard deviation of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).stdev()
        1.0
        """
        return self.into(statistics.stdev)

    @overload
    def variance[U: int | float](
        self: Iter[U],
    ) -> float: ...
    @overload
    def variance(self: Expr) -> Expr: ...
    def variance(self):
        """
        Return the variance of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 7, 8]).variance()
        9.7
        """
        return self.into(statistics.variance)
