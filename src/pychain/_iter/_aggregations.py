from __future__ import annotations

import functools
import statistics
from collections.abc import Callable, Iterable
from typing import Literal

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper


class BaseAgg[T](IterWrapper[T]):
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
        return self.into(functools.partial(functools.reduce, func))

    def combination_index(self, r: Iterable[T]) -> int:
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

    def first(self) -> T:
        """
        Return the first element.

            >>> from pychain import Iter
            >>> Iter([9]).first()
            9
        """
        return self.into(cz.itertoolz.first)

    def second(self) -> T:
        """
        Return the second element.

            >>> from pychain import Iter
            >>> Iter([9, 8]).second()
            8
        """
        return self.into(cz.itertoolz.second)

    def last(self) -> T:
        """
        Return the last element.

            >>> from pychain import Iter
            >>> Iter([7, 8, 9]).last()
            9
        """
        return self.into(cz.itertoolz.last)

    def length(self) -> int:
        """
        Return the length of the sequence.
        Like the builtin len but works on lazy sequences.

            >>> from pychain import Iter
            >>> Iter([1, 2]).length()
            2
        """
        return self.into(cz.itertoolz.count)

    def item(self, index: int) -> T:
        """
        Return item at index.

        >>> from pychain import Iter
        >>> Iter([10, 20]).item(1)
        20
        """
        return self.into(functools.partial(cz.itertoolz.nth, index))

    def argmax[U](self, key: Callable[[T], U] | None = None) -> int:
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
        >>> accuracy.into(max)
        84
        """
        return self.into(mit.argmax, key=key)

    def argmin[U](self, key: Callable[[T], U] | None = None) -> int:
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
        >>> ages.into(min, key=cost)
        10
        """
        return self.into(mit.argmin, key=key)

    def sum[U: int | float](self: IterWrapper[U]) -> U | Literal[0]:
        """
        Return the sum of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).sum()
        6
        """
        return self.into(sum)

    def min[U: int | float](self: IterWrapper[U]) -> U:
        """
        Return the minimum of the sequence.

        >>> from pychain import Iter
        >>> Iter([3, 1, 2]).min()
        1
        """
        return self.into(min)

    def max[U: int | float](self: IterWrapper[U]) -> U:
        """
        Return the maximum of the sequence.

        >>> from pychain import Iter
        >>> Iter([3, 1, 2]).max()
        3
        """
        return self.into(max)

    def mean[U: int | float](self: IterWrapper[U]) -> float:
        """
        Return the mean of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).mean()
        2
        """
        return self.into(statistics.mean)

    def median[U: int | float](self: IterWrapper[U]) -> float:
        """
        Return the median of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 3, 2]).median()
        2
        """
        return self.into(statistics.median)

    def mode[U: int | float](self: IterWrapper[U]) -> U:
        """
        Return the mode of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 2, 3]).mode()
        2
        """
        return self.into(statistics.mode)

    def stdev[U: int | float](
        self: IterWrapper[U],
    ) -> float:
        """
        Return the standard deviation of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).stdev()
        1.0
        """
        return self.into(statistics.stdev)

    def variance[U: int | float](
        self: IterWrapper[U],
    ) -> float:
        """
        Return the variance of the sequence.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 7, 8]).variance()
        9.7
        """
        return self.into(statistics.variance)
