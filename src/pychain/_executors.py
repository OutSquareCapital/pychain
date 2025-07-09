from dataclasses import dataclass
from collections.abc import Callable, Iterable
import functools as ft
import cytoolz as cz
import polars as pl
import functional as fn  # type: ignore
import numpy as np
from numpy.typing import NDArray
from typing import TYPE_CHECKING, Any
from ._lazyfuncs import (
    TransformFunc,
    CheckFunc,
)
from collections import deque

if TYPE_CHECKING:
    from ._implementations import ScalarChain


@dataclass(slots=True, frozen=True)
class GetterBase[V]:
    _value: Iterable[V]

    def __call__[V1](self, f: TransformFunc[Iterable[V], V1]) -> "ScalarChain[V1]":
        """
        Apply a function to the iterable and return a ScalarChain.
        """
        raise NotImplementedError

    def first(self) -> "ScalarChain[V]":
        """
        Return the first element of the iterable (see cytoolz.first).

        Example:
            >>> GetterBase([1, 2, 3]).first().unwrap()
            1
        """
        return self(f=cz.itertoolz.first)

    def second(self) -> "ScalarChain[V]":
        """
        Return the second element of the iterable (see cytoolz.second).

        Example:
            >>> GetterBase([1, 2, 3]).second().unwrap()
            2
        """
        return self(f=cz.itertoolz.second)

    def last(self) -> "ScalarChain[V]":
        """
        Return the last element of the iterable (see cytoolz.last).

        Example:
            >>> GetterBase([1, 2, 3]).last().unwrap()
            3
        """
        return self(f=cz.itertoolz.last)

    def at_index(self, index: int) -> "ScalarChain[V]":
        """
        Return the element at the given index (see cytoolz.nth).

        Example:
            >>> GetterBase([1, 2, 3]).at_index(1).unwrap()
            2
        """
        return self(f=ft.partial(cz.itertoolz.nth, n=index))

    def len(self) -> "ScalarChain[int]":
        """
        Return the length of the iterable (see cytoolz.count).

        Example:
            >>> GetterBase([1, 2, 3]).len().unwrap()
            3
        """
        return self(f=cz.itertoolz.count)


@dataclass(slots=True, frozen=True)
class Checker[V]:
    """
    Checker provides boolean checks for iterables, such as all, any, distinct, and iterable.
    Enables validation and inspection of iterables in a chainable way.
    """

    _value: Iterable[V]

    def __call__[V1](self, f: CheckFunc[Iterable[V]]) -> bool:
        """
        Apply a boolean function to the iterable.
        """
        return f(self._value)

    def all(self) -> bool:
        """
        Return True if all elements are truthy (see built-in all).

        Example:
            >>> Checker([1, 2, 3]).all()
            True
        """
        return all(self._value)

    def any(self) -> bool:
        """
        Return True if any element is truthy (see built-in any).

        Example:
            >>> Checker([0, 1, 2]).any()
            True
        """
        return any(self._value)

    def distinct(self) -> bool:
        """
        Return True if all elements are distinct (see cytoolz.isdistinct).

        Example:
            >>> Checker([1, 2, 2]).distinct()
            False
        """
        return cz.itertoolz.isdistinct(self._value)

    def iterable(self) -> bool:
        """
        Return True if the value is iterable (see cytoolz.isiterable).

        Example:
            >>> Checker([1, 2, 3]).iterable()
            True
        """
        return cz.itertoolz.isiterable(self._value)


@dataclass(slots=True, frozen=True)
class Converter[V]:
    """
    Converter provides utility methods to transform and consume an iterable of values.
    Useful for converting the result of a chain to a concrete collection or data structure.
    """

    _value: Iterable[V]

    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> Any:
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
            >>> Converter([1, 2, 3]).series()
            shape: (3,)
            Series: '' [i64]
            [1, 2, 3]
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

    def functional(self):  # type: ignore
        """
        Convert the iterable into a functional sequence using the `fn` library.

        Example:
            >>> Converter([1, 2, 3]).functional().map(lambda x: x * 2).to_list()
            [2, 4, 6]
        """
        return fn.seq(self._value)  # type: ignore
