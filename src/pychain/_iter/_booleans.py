from __future__ import annotations

from collections.abc import Callable

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper


class BaseBool[T](IterWrapper[T]):
    def all(self) -> bool:
        """
        Return True if all items are truthy.
            >>> import pychain as pc
            >>> pc.Iter([1, True]).all()
            True
        """
        return self.into(all)

    def any(self) -> bool:
        """
        Return True if any item is truthy.
            >>> import pychain as pc
            >>> pc.Iter([0, 1]).any()
            True
        """
        return self.into(any)

    def is_distinct(self) -> bool:
        """
        Return True if all items are distinct.

        >>> import pychain as pc
        >>> pc.Iter([1, 2]).is_distinct()
        True
        """
        return self.into(cz.itertoolz.isdistinct)

    def all_equal[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Return True if all items are equal.

        >>> import pychain as pc
        >>> pc.Iter([1, 1, 1]).all_equal()
        True

        A function that accepts a single argument and returns a transformed version of each input item can be specified with key:

        >>> pc.Iter("AaaA").all_equal(key=str.casefold)
        True
        >>> pc.Iter([1, 2, 3]).all_equal(key=lambda x: x < 10)
        True
        """
        return self.into(mit.all_equal, key=key)

    def all_unique[U](self, key: Callable[[T], U] | None = None) -> bool:
        """
        Returns True if all the elements of iterable are unique (no two elements are equal).

        >>> import pychain as pc
        >>> pc.Iter("ABCB").all_unique()
        False

        If a key function is specified, it will be used to make comparisons.

        >>> pc.Iter("ABCb").all_unique()
        True

        >>> pc.Iter("ABCb").all_unique(str.lower)
        False

        The function returns as soon as the first non-unique element is encountered.

        Iterables with a mix of hashable and unhashable items can be used, but the function will be slower for unhashable items

        """
        return self.into(mit.all_unique, key=key)

    def is_sorted[U](
        self,
        key: Callable[[T], U] | None = None,
        reverse: bool = False,
        strict: bool = False,
    ) -> bool:
        """
        Returns True if the items of iterable are in sorted order, and False otherwise.

        Key and reverse have the same meaning that they do in the built-in sorted function.

        >>> import pychain as pc
        >>> pc.Iter(["1", "2", "3", "4", "5"]).is_sorted(key=int)
        True
        >>> pc.Iter([5, 4, 3, 1, 2]).is_sorted(reverse=True)
        False

        If strict, tests for strict sorting, that is, returns False if equal elements are found:

        >>> pc.Iter([1, 2, 2]).is_sorted()
        True
        >>> pc.Iter([1, 2, 2]).is_sorted(strict=True)
        False

        The function returns False after encountering the first out-of-order item.

        This means it may produce results that differ from the built-in sorted function for objects with unusual comparison dynamics (like math.nan).

        If there are no out-of-order items, the iterable is exhausted.
        """
        return self.into(mit.is_sorted, key=key, reverse=reverse, strict=strict)
