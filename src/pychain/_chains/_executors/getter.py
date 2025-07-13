from collections.abc import Callable, Iterable
from dataclasses import dataclass

from ..._fn import agg


@dataclass(slots=True, frozen=True)
class Getter[V]:
    _value: Iterable[V]
    """
    Extract elements or properties from an iterable in a chainable way.
    """

    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> V1:
        return f(self._value)

    def first(self) -> V:
        """
        Return the first element of the iterable (see cytoolz.first).

        Example:
            >>> Getter([1, 2, 3]).first()
            1
        """
        return self(f=agg.first)

    def second(self) -> V:
        """
        Return the second element of the iterable (see cytoolz.second).

        Example:
            >>> Getter([1, 2, 3]).second()
            2
        """
        return self(f=agg.second)

    def last(self) -> V:
        """
        Return the last element of the iterable (see cytoolz.last).

        Example:
            >>> Getter([1, 2, 3]).last()
            3
        """
        return self(f=agg.last)

    def at_index(self, index: int) -> V:
        """
        Return the element at the given index (see cytoolz.nth).

        Example:
            >>> Getter([1, 2, 3]).at_index(1)
            2
        """
        return self(f=agg.at_index(index=index))

    def len(self) -> int:
        """
        Return the length of the iterable (see cytoolz.count).

        Example:
            >>> Getter([1, 2, 3]).len()
            3
        """
        return self(f=agg.length)
