from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self

from ._core import CommonBase, iter_on

if TYPE_CHECKING:
    from ._iter import Iter


class List[T](CommonBase[list[T]]):
    _data: list[T]
    __slots__ = ("_data",)

    def transform[**P, U](
        self,
        func: Callable[Concatenate[list[T], P], list[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "List[U]":
        return List(func(self._data, *args, **kwargs))

    def into_iter(self) -> "Iter[T]":
        """Return an iterator over the list's elements."""

        return iter_on(iter(self._data))

    def clear(self) -> Self:
        """
        Clear the list and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).clear()
            []
        """
        self._data.clear()
        return self

    def insert(self, index: int, value: T) -> Self:
        """
        Insert an object into the list at the specified index and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).insert(1, 3)
            [1, 3, 2]
        """
        self._data.insert(index, value)
        return self

    def copy(self) -> Self:
        """
        Return a shallow copy of the list.

        Example:
            >>> List([1, 2]).copy()
            [1, 2]
        """
        return self.__class__(self._data.copy())

    def append(self, value: T) -> Self:
        """
        Append object to the end of the list and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).append(3)
            [1, 2, 3]
        """
        self._data.append(value)
        return self

    def extend(self, *others: Iterable[T]) -> Self:
        """
        Extend the list with elements from another iterable and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).extend([3, 4])
            [1, 2, 3, 4]
        """
        self._data.extend(*others)
        return self

    def remove(self, value: T) -> Self:
        """
        Remove an object from the list and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).remove(2)
            [1]
        """
        self._data.remove(value)
        return self

    def reverse(self) -> Self:
        """
        Reverse the order of the list and return self for convenience.

        **Warning**: Mutates the original list.

        Example:
            >>> List([1, 2]).reverse()
            [2, 1]
        """
        self._data.reverse()
        return self
