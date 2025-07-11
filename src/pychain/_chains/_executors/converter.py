from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np
import polars as pl
from numpy.typing import NDArray


@dataclass(slots=True, frozen=True)
class Converter[V]:
    """
    Converter provides utility methods to transform and consume an iterable of values.
    Useful for converting the result of a chain to a concrete collection or data structure.
    """

    _value: Iterable[V]

    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> V1:
        """
        Apply a function to the iterable and return the result.
        """
        return f(self._value)

    def consumed(self) -> None:
        """
        Consume the iterable by iterating through all its elements (useful for exhaust generators).
        """
        for _ in self._value:
            pass

    def list(self) -> list[V]:
        """
        Convert the iterable into a list.

        Example:
            >>> Converter([1, 2, 3]).list()
            [1, 2, 3]
        """
        return list(self._value)

    def set(self) -> set[V]:
        """
        Convert the iterable into a set.

        Example:
            >>> Converter([1, 2, 2, 3]).set()
            {1, 2, 3}
        """
        return set(self._value)

    def tuple(self) -> tuple[V, ...]:
        """
        Convert the iterable into a tuple.

        Example:
            >>> Converter([1, 2, 3]).tuple()
            (1, 2, 3)
        """
        return tuple(self._value)

    def deque(self) -> deque[V]:
        """
        Convert the iterable into a deque (collections.deque).

        Example:
            >>> Converter([1, 2, 3]).deque()
            deque([1, 2, 3])
        """
        return deque(self._value)

    def dict(self):
        """
        Convert the iterable into a dictionary (see built-in dict).

        Example:
            >>> Converter([("a", 1), ("b", 2)]).dict()
            {'a': 1, 'b': 2}
        """
        return dict(self._value)  # type: ignore

    def array(self) -> NDArray[Any]:
        """
        Convert the iterable into a NumPy array.

        Example:
            >>> Converter([1, 2, 3]).array()
            array([1, 2, 3])
        """
        return np.array(self._value)

    def series(self) -> pl.Series:
        """
        Convert the iterable into a Polars Series.

        Example:
            >>> Converter([1, 2, 3]).series().shape
            (3,)
        """
        return pl.Series(values=self._value)

    def dataframe(self) -> pl.DataFrame:
        """
        Convert the iterable into a Polars DataFrame.

        Example:
            >>> Converter({"a": [1, 2], "b": [3, 4]}).dataframe()
            shape: (2, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 3   │
            │ 2   ┆ 4   │
            └─────┴─────┘
        """
        return pl.DataFrame(data=self._value)

    def lazyframe(self) -> pl.LazyFrame:
        """
        Convert the iterable into a Polars LazyFrame.

        Example:
            >>> Converter({"a": [1, 2], "b": [3, 4]}).lazyframe()  # doctest: +SKIP
            <class 'polars.lazyframe.frame.LazyFrame'>
        """
        return pl.LazyFrame(data=self._value)
