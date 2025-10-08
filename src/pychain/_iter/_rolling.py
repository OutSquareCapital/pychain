from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import rolling

from .._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._main import Iter


class IterRolling[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def rolling_mean(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling mean.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5]).rolling_mean(3).into(list)
        [2.0, 3.0, 4.0]
        """
        return iter_factory(rolling.Mean(self._data, window_size))

    def rolling_median(self, window_size: int) -> Iter[T]:
        """
        Compute the rolling median.

        >>> from pychain import Iter
        >>> Iter([1, 3, 2, 5, 4]).rolling_median(3).into(list)
        [2, 3, 4]
        """
        return iter_factory(rolling.Median(self._data, window_size))

    def rolling_sum(self, window_size: int) -> Iter[T]:
        """
        Compute the rolling sum.

        Will return integers if the input is integers, floats if the input is floats or mixed.

        >>> from pychain import Iter
        >>> Iter([1.0, 2, 3, 4, 5]).rolling_sum(3).into(list)
        [6.0, 9.0, 12.0]
        """
        return iter_factory(rolling.Sum(self._data, window_size))

    def rolling_min(self, window_size: int) -> Iter[T]:
        """
        Compute the rolling minimum.

        >>> from pychain import Iter
        >>> Iter([3, 1, 4, 1, 5, 9, 2]).rolling_min(3).into(list)
        [1, 1, 1, 1, 2]
        """
        return iter_factory(rolling.Min(self._data, window_size))

    def rolling_max(self, window_size: int) -> Iter[T]:
        """
        Compute the rolling maximum.

        >>> from pychain import Iter
        >>> Iter([3, 1, 4, 1, 5, 9, 2]).rolling_max(3).into(list)
        [4, 4, 5, 9, 9]
        """
        return iter_factory(rolling.Max(self._data, window_size))

    def rolling_var(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling variance.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling_var(3).map(lambda x: round(x, 2)).into(list)
        [2.33, 2.33, 3.0]
        """
        return iter_factory(rolling.Var(self._data, window_size))

    def rolling_std(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling standard deviation.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling_std(3).map(lambda x: round(x, 2)).into(list)
        [1.53, 1.53, 1.73]
        """
        return iter_factory(rolling.Std(self._data, window_size))

    def rolling_kurtosis(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling kurtosis.
        The windows must have at least 4 observations.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling_kurtosis(4).into(list)
        [1.5, -3.901234567901234]
        """
        return iter_factory(rolling.Kurtosis(self._data, window_size))

    def rolling_skew(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling skewness.
        The windows must have at least 3 observations.

        >>> from pychain import Iter
        >>> Iter([1, 2, 4, 1, 4]).rolling_skew(3).map(lambda x: round(x, 2)).into(list)
        [0.94, 0.94, -1.73]
        """
        return iter_factory(rolling.Skew(self._data, window_size))

    def rolling_all(self, window_size: int) -> Iter[bool]:
        """
        Compute whether all values in the window evaluate to True.

        >>> from pychain import Iter
        >>> Iter([True, True, False, True, True]).rolling_all(2).into(list)
        [True, False, False, True]
        """
        return iter_factory(rolling.All(self._data, window_size))

    def rolling_any(self, window_size: int) -> Iter[bool]:
        """
        Compute whether any value in the window evaluates to True.

        >>> from pychain import Iter
        >>> Iter([True, True, False, True, True]).rolling_any(2).into(list)
        [True, True, True, True]
        """
        return iter_factory(rolling.Any(self._data, window_size))

    def rolling_product(self, window_size: int) -> Iter[float]:
        """
        Compute the rolling product.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5]).rolling_product(3).into(list)
        [6.0, 24.0, 60.0]
        """
        return iter_factory(rolling.Product(self._data, window_size))

    def rolling_apply[R](
        self, func: Callable[[Iterable[T]], R], window_size: int
    ) -> Iter[R]:
        """
        Apply a custom function to each rolling window.

        The function should accept an iterable and return a single value.

        >>> from pychain import Iter
        >>> import rolling
        >>> def range_func(window):
        ...     return max(window) - min(window)
        >>> Iter([1, 3, 2, 5, 4]).rolling_apply(range_func, 3).into(list)
        [2, 3, 3]
        """
        return iter_factory(rolling.Apply(self._data, window_size, "fixed", func))

    def rolling_apply_pairwise[R](
        self, other: Iterable[T], func: Callable[[T, T], R], window_size: int
    ) -> Iter[R]:
        """
        Apply a custom pairwise function to each rolling window of size 2.

        The function should accept two arguments and return a single value.

        >>> from pychain import Iter
        >>> from statistics import correlation
        >>> seq_1 = [1, 2, 3, 4, 5]
        >>> seq_2 = [1, 2, 3, 2, 1]
        >>> Iter(seq_1).rolling_apply_pairwise(seq_2, correlation, 3).into(list)
        [1.0, 0.0, -1.0]
        """
        return iter_factory(rolling.ApplyPairwise(self._data, other, window_size, func))
