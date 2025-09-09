from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self


@dataclass(slots=True)
class BaseList[T]:
    _data: list[T]

    def clear(self) -> Self:
        """
        Clear the list and return self for convenience.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).clear().unwrap()
            []
        """
        self._data.clear()
        return self

    def insert(self, index: int, value: T) -> Self:
        """
        Insert an object into the list at the specified index and return self for convenience.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).insert(1, 3).unwrap()
            [1, 3, 2]
        """
        self._data.insert(index, value)
        return self

    def copy(self) -> Self:
        """
        Return a shallow copy of the list.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).copy().unwrap()
            [1, 2]
        """
        return self.__class__(self._data.copy())

    def append(self, value: T) -> Self:
        """
        Append object to the end of the list and return self for convenience.

        **Warning**: Mutates the original list.
        Example:
            >>> from ._lib import List
            >>> List([1, 2]).append(3).unwrap()
            [1, 2, 3]
        """
        self._data.append(value)
        return self

    def extend(self, other: Iterable[T]) -> Self:
        """
        Extend the list with elements from another iterable and return self for convenience.

        **Warning**: Mutates the original list.
        Example:
            >>> from ._lib import List
            >>> List([1, 2]).extend([3, 4]).unwrap()
            [1, 2, 3, 4]
        """
        self._data.extend(other)
        return self

    def remove(self, value: T) -> Self:
        """
        Remove an object from the list and return self for convenience.

        **Warning**: Mutates the original list.
        Example:
            >>> from ._lib import List
            >>> List([1, 2]).remove(2).unwrap()
            [1]
        """
        self._data.remove(value)
        return self

    def reverse(self) -> Self:
        """
        Reverse the order of the list and return self for convenience.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).reverse().unwrap()
            [2, 1]
        """
        self._data.reverse()
        return self
