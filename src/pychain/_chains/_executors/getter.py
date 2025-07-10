from collections.abc import Callable, Iterable
from dataclasses import dataclass
import functools as ft
import cytoolz as cz


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
            >>> BaseGetter([1, 2, 3]).first().unwrap()
            1
        """
        return self(f=cz.itertoolz.first)

    def second(self) -> V:
        """
        Return the second element of the iterable (see cytoolz.second).

        Example:
            >>> BaseGetter([1, 2, 3]).second().unwrap()
            2
        """
        return self(f=cz.itertoolz.second)

    def last(self) -> V:
        """
        Return the last element of the iterable (see cytoolz.last).

        Example:
            >>> BaseGetter([1, 2, 3]).last().unwrap()
            3
        """
        return self(f=cz.itertoolz.last)

    def at_index(self, index: int) -> V:
        """
        Return the element at the given index (see cytoolz.nth).

        Example:
            >>> BaseGetter([1, 2, 3]).at_index(1).unwrap()
            2
        """
        return self(f=ft.partial(cz.itertoolz.nth, index))

    def len(self) -> int:
        """
        Return the length of the iterable (see cytoolz.count).

        Example:
            >>> BaseGetter([1, 2, 3]).len().unwrap()
            3
        """
        return self(f=cz.itertoolz.count)
