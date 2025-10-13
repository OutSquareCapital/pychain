from collections.abc import Callable

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper


class IterBool[T](IterWrapper[T]):
    def is_not_empty(self) -> bool:
        """
        Return True if the iterable is not empty.

            >>> from pychain import Iter
            >>> Iter([1]).is_not_empty()
            True
        """
        return True if self._data else False

    def is_empty(self) -> bool:
        """
        Return True if the iterable is empty.

            >>> from pychain import Iter
            >>> Iter([]).is_empty()
            True
        """
        return False if self._data else True

    def is_distinct(self) -> bool:
        """
        Return True if all items are distinct.

            >>> from pychain import Iter
            >>> Iter([1, 2]).is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """
        Return True if all items are truthy.

            >>> from pychain import Iter
            >>> Iter([1, True]).all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """
        Return True if any item is truthy.

            >>> from pychain import Iter
            >>> Iter([0, 1]).any()
            True
        """
        return any(self._data)

    def all_equal[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Return True if all items are equal.

            >>> from pychain import Iter
            >>> Iter([1, 1, 1]).all_equal()
            True
        """
        return mit.all_equal(self._data, key=key)

    def all_unique[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Returns True if all the elements of iterable are unique (no two elements are equal).

        >>> from pychain import Iter
        >>> Iter("ABCB").all_unique()
        False

        If a key function is specified, it will be used to make comparisons.

        >>> Iter("ABCb").all_unique()
        True

        >>> Iter("ABCb").all_unique(str.lower)
        False

        The function returns as soon as the first non-unique element is encountered.
        Iterables with a mix of hashable and unhashable items can be used, but the function will be slower for unhashable items

        """
        return mit.all_unique(self._data, key=key)

    def is_sorted[U](
        self,
        key: Callable[[T], U] | None = None,
        reverse: bool = False,
        strict: bool = False,
    ) -> bool:
        """
        Returns True if the items of iterable are in sorted order, and False otherwise.

        Key and reverse have the same meaning that they do in the built-in sorted function.

        >>> from pychain import Iter
        >>> Iter(["1", "2", "3", "4", "5"]).is_sorted(key=int)
        True
        >>> Iter([5, 4, 3, 1, 2]).is_sorted(reverse=True)
        False

        If strict, tests for strict sorting, that is, returns False if equal elements are found:

        >>> Iter([1, 2, 2]).is_sorted()
        True
        >>> Iter([1, 2, 2]).is_sorted(strict=True)
        False

        The function returns False after encountering the first out-of-order item.

        This means it may produce results that differ from the built-in sorted function for objects with unusual comparison dynamics (like math.nan).

        If there are no out-of-order items, the iterable is exhausted.
        """
        return mit.is_sorted(self._data, key=key, reverse=reverse, strict=strict)
