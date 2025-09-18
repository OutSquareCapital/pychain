from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import rolling

from .._core import iter_factory

if TYPE_CHECKING:
    from ._main import Iter


@dataclass(slots=True)
class RollingNameSpace[T]:
    _parent: Iterable[T]
    _window: int

    def mean(self) -> Iter[float]:
        """
        Compute the rolling mean.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5]).rolling(3).mean().to_list()
        [2.0, 3.0, 4.0]
        """
        return iter_factory(rolling.Mean(self._parent, self._window))

    def median(self) -> Iter[T]:
        """
        Compute the rolling median.

        >>> from pychain import Iter
        >>> Iter([1, 3, 2, 5, 4]).rolling(3).median().to_list()
        [2, 3, 4]
        """
        return iter_factory(rolling.Median(self._parent, self._window))

    def sum(self) -> Iter[T]:
        """
        Compute the rolling sum.

        Will return integers if the input is integers, floats if the input is floats or mixed.

        >>> from pychain import Iter
        >>> Iter([1.0, 2, 3, 4, 5]).rolling(3).sum().to_list()
        [6.0, 9.0, 12.0]
        """
        return iter_factory(rolling.Sum(self._parent, self._window))

    def min(self) -> Iter[T]:
        """
        Compute the rolling minimum.

        >>> from pychain import Iter
        >>> Iter([3, 1, 4, 1, 5, 9, 2]).rolling(3).min().to_list()
        [1, 1, 1, 1, 2]
        """
        return iter_factory(rolling.Min(self._parent, self._window))

    def max(self) -> Iter[T]:
        """
        Compute the rolling maximum.

        >>> from pychain import Iter
        >>> Iter([3, 1, 4, 1, 5, 9, 2]).rolling(3).max().to_list()
        [4, 4, 5, 9, 9]
        """
        return iter_factory(rolling.Max(self._parent, self._window))

    def var(self) -> Iter[float]:
        """
        Compute the rolling variance.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling(3).var().map(lambda x: round(x, 2)).to_list()
        [2.33, 2.33, 3.0]
        """
        return iter_factory(rolling.Var(self._parent, self._window))

    def std(self) -> Iter[float]:
        """
        Compute the rolling standard deviation.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling(3).std().map(lambda x: round(x, 2)).to_list()
        [1.53, 1.53, 1.73]
        """
        return iter_factory(rolling.Std(self._parent, self._window))

    def kurtosis(self) -> Iter[float]:
        """
        Compute the rolling kurtosis.
        The windows must have at least 4 observations.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling(4).kurtosis().to_list()
        [1.5, -3.901234567901234]
        """
        return iter_factory(rolling.Kurtosis(self._parent, self._window))

    def skew(self) -> Iter[float]:
        """
        Compute the rolling skewness.
        The windows must have at least 3 observations.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling(3).skew().map(lambda x: round(x, 2)).to_list()
        [0.94, 0.94, -1.73]
        """
        return iter_factory(rolling.Skew(self._parent, self._window))

    def all(self) -> Iter[bool]:
        """
        Compute whether all values in the window evaluate to True.

        >>> from pychain import Iter
        >>> Iter([True, True, False, True, True]).rolling(2).all().to_list()
        [True, False, False, True]
        """
        return iter_factory(rolling.All(self._parent, self._window))

    def any(self) -> Iter[bool]:
        """
        Compute whether any value in the window evaluates to True.

        >>> from pychain import Iter
        >>> Iter([True, True, False, True, True]).rolling(2).any().to_list()
        [True, True, True, True]
        """
        return iter_factory(rolling.Any(self._parent, self._window))

    def product(self) -> Iter[float]:
        """
        Compute the rolling product.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5]).rolling(3).product().to_list()
        [6.0, 24.0, 60.0]
        """
        return iter_factory(rolling.Product(self._parent, self._window))

    def apply[R](self, func: Callable[[Iterable[T]], R]) -> Iter[R]:
        """
        Apply a custom function to each rolling window.

        The function should accept an iterable and return a single value.

        >>> from pychain import Iter
        >>> import rolling
        >>> def range_func(window):
        ...     return max(window) - min(window)
        >>> Iter([1, 3, 2, 5, 4]).rolling(3).apply(range_func).to_list()
        [2, 3, 3]
        """
        return iter_factory(rolling.Apply(self._parent, self._window, "fixed", func))

    def apply_pairwise[R](
        self, other: Iterable[T], func: Callable[[T, T], R]
    ) -> Iter[R]:
        """
        Apply a custom pairwise function to each rolling window of size 2.

        The function should accept two arguments and return a single value.

        >>> from pychain import Iter
        >>> from statistics import correlation
        >>> seq_1 = [1, 2, 3, 4, 5]
        >>> seq_2 = [1, 2, 3, 2, 1]
        >>> Iter(seq_1).rolling(3).apply_pairwise(seq_2, correlation).to_list()
        [1.0, 0.0, -1.0]
        """
        return iter_factory(
            rolling.ApplyPairwise(self._parent, other, self._window, func)
        )
