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
    """
    GetterBase provides methods to extract elements or properties from an iterable.
    Useful for retrieving specific elements or properties in a chainable way.

    Example:
        >>> getter = GetterBase([1, 2, 3])
        >>> getter.first()  # Returns 1
        >>> getter.last()  # Returns 3
        >>> getter.at_index(1)  # Returns 2
        >>> getter.len()  # Returns 3
    """

    _value: Iterable[V]

    def __call__[V1](self, f: TransformFunc[Iterable[V], V1]) -> "ScalarChain[V1]":
        """
        Apply a function to the iterable and return a ScalarChain.
        """
        raise NotImplementedError

    def first(self) -> "ScalarChain[V]":
        """
        Return the first element of the iterable (see cytoolz.first).
        """
        return self(f=cz.itertoolz.first)

    def second(self) -> "ScalarChain[V]":
        """
        Return the second element of the iterable (see cytoolz.second).
        """
        return self(f=cz.itertoolz.second)

    def last(self) -> "ScalarChain[V]":
        """
        Return the last element of the iterable (see cytoolz.last).
        """
        return self(f=cz.itertoolz.last)

    def at_index(self, index: int) -> "ScalarChain[V]":
        """
        Return the element at the given index (see cytoolz.nth).
        """
        return self(f=ft.partial(cz.itertoolz.nth, n=index))

    def len(self) -> "ScalarChain[int]":
        """
        Return the length of the iterable (see cytoolz.count).
        """
        return self(f=cz.itertoolz.count)


@dataclass(slots=True, frozen=True)
class Checker[V]:
    """
    Checker provides boolean checks for iterables, such as all, any, distinct, and iterable.
    Enables validation and inspection of iterables in a chainable way.

    Example:
        >>> Checker([1, 2, 3]).all()  # True
        >>> Checker([0, 1, 2]).any()  # True
        >>> Checker([1, 2, 2]).distinct()  # False
        >>> Checker([1, 2, 3]).iterable()  # True
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
        """
        return all(self._value)

    def any(self) -> bool:
        """
        Return True if any element is truthy (see built-in any).
        """
        return any(self._value)

    def distinct(self) -> bool:
        """
        Return True if all elements are distinct (see cytoolz.isdistinct).
        """
        return cz.itertoolz.isdistinct(self._value)

    def iterable(self) -> bool:
        """
        Return True if the value is iterable (see cytoolz.isiterable).
        """
        return cz.itertoolz.isiterable(self._value)


@dataclass(slots=True, frozen=True)
class Converter[V]:
    """
    Converter provides utility methods to transform and consume an iterable of values.
    Useful for converting the result of a chain to a concrete collection or data structure.

    Example:
        >>> Converter([1, 2, 3]).list()  # [1, 2, 3]
        >>> Converter([1, 2, 2, 3]).set()  # {1, 2, 3}
        >>> Converter([("a", 1), ("b", 2)]).dict()  # {'a': 1, 'b': 2}
        >>> Converter([1, 2, 3]).array()  # array([1, 2, 3])
        >>> Converter([1, 2, 3]).series()  # pl.Series([1, 2, 3])
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
        """
        return list(self._value)

    def set(self) -> set[V]:
        """
        Convert the iterable into a set.
        """
        return set(self._value)

    def tuple(self) -> tuple[V, ...]:
        """
        Convert the iterable into a tuple.
        """
        return tuple(self._value)

    def deque(self) -> deque[V]:
        """
        Convert the iterable into a deque (collections.deque).
        """
        return deque(self._value)

    def dict(self):
        """
        Convert the iterable into a dictionary (see built-in dict).
        """
        return dict(self._value)  # type: ignore

    def array(self) -> NDArray[Any]:
        """
        Convert the iterable into a NumPy array.
        """
        return np.array(self._value)

    def series(self) -> pl.Series:
        """
        Convert the iterable into a Polars Series.
        """
        return pl.Series(values=self._value)

    def dataframe(self) -> pl.DataFrame:
        """
        Convert the iterable into a Polars DataFrame.
        """
        return pl.DataFrame(data=self._value)

    def lazyframe(self) -> pl.LazyFrame:
        """
        Convert the iterable into a Polars LazyFrame.
        """
        return pl.LazyFrame(data=self._value)

    def functional(self):  # type: ignore
        """
        Convert the iterable into a functional sequence using the `fn` library.
        """
        return fn.seq(self._value)  # type: ignore
