from dataclasses import dataclass
from collections.abc import Callable, Iterable
from typing import Any, Literal
from functools import partial
import statistics as stats


@dataclass(slots=True, frozen=True)
class Aggregator[T]:
    _value: Iterable[T]

    def __call__(self, on: Callable[[Iterable[Any]], Any]):
        return on(self._value)

    def mean(self) -> float | int:
        """
        Calculate the mean of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).mean()
            3.3333333333333335
        """
        return self(stats.mean)

    def median(self) -> float | int:
        """
        Calculate the median of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).median()
            3.5
        """
        return self(stats.median)

    def mode(self) -> T:
        """
        Calculate the mode of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).mode()
            5
        """
        return self(stats.mode)

    def stdev(self) -> float | int:
        """
        Calculate the sample standard deviation of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).stdev()
            1.5811388300841898
        """
        return self(stats.stdev)

    def variance(self) -> float | int:
        """
        Calculate the sample variance of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).variance()
            2.5
        """
        return self(stats.variance)

    def pvariance(self) -> float | int:
        """
        Calculate the population variance of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).pvariance()
            2.2222222222222223
        """
        return self(stats.pvariance)

    def quantiles(
        self, n: int, method: Literal["inclusive", "exclusive"]
    ) -> list[float | int]:
        """
        Calculate quantiles of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).quantiles(4, "inclusive")
            [2.0, 3.0, 4.0]

            >>> Aggregator([1, 2, 3, 4, 5]).quantiles(4, "exclusive")
            [1.5, 3.0, 4.5]
        """
        return self(partial(stats.quantiles, n=n, method=method))

    def median_low(self) -> float | int:
        """
        Calculate the low median of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).median_low()
            3
        """
        return self(stats.median_low)

    def median_high(self) -> float | int:
        """
        Calculate the high median of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).median_high()
            4
        """
        return self(stats.median_high)

    def median_grouped(self) -> float:
        """
        Calculate the median of grouped data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5, 5]).median_grouped()
            3.5
        """
        return self(stats.median_grouped)

    def sum(self) -> T:
        """
        Calculate the sum of the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).sum()
            15
        """
        return self(sum)

    def min(self) -> T:
        """
        Find the minimum value in the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).min()
            1
        """
        return self(min)

    def max(self) -> T:
        """
        Find the maximum value in the input data.

        Example:
            >>> Aggregator([1, 2, 3, 4, 5]).max()
            5
        """
        return self(max)
