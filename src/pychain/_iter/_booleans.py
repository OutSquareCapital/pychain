from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper


class BaseBool[T](IterWrapper[T]):
    def all(self) -> bool:
        """
        Return True if bool(x) is True for all values x in the iterable.

        If the iterable is empty, return True.
        >>> import pychain as pc
        >>> pc.Iter([1, True]).all()
        True
        >>> pc.Iter([]).all()
        True
        >>> pc.Iter([1, 0]).all()
        False
        """
        return self.into(all)

    def not_all(self) -> bool:
        """
        Return True if not all items are truthy.

        If the iterable is empty, return False.
        >>> import pychain as pc
        >>> pc.Iter([1, 0]).not_all()
        True
        >>> pc.Iter([1, True]).not_all()
        False
        >>> pc.Iter([]).not_all()
        False
        """

        def _not_all(data: Iterable[T]) -> bool:
            return not all(data)

        return self.into(_not_all)

    def any(self) -> bool:
        """
        Return True if bool(x) is True for any x in the iterable.

        If the iterable is empty, return False.
        >>> import pychain as pc
        >>> pc.Iter([0, 1]).any()
        True
        >>> pc.Iter.from_(range(0)).any()
        False
        """
        return self.into(any)

    def not_any(self) -> bool:
        """
        Return True if no items are truthy.

        If the iterable is empty, return True.
        >>> import pychain as pc
        >>> pc.Iter([0, False]).not_any()
        True
        >>> pc.Iter([0, 1]).not_any()
        False
        >>> pc.Iter([]).not_any()
        True
        """

        def _not_any(data: Iterable[T]) -> bool:
            return not any(data)

        return self.into(_not_any)

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

    @overload
    def first_true(
        self, default: None = None, predicate: Callable[[T], bool] | None = ...
    ) -> T | None: ...
    @overload
    def first_true(
        self, default: T, predicate: Callable[[T], bool] | None = ...
    ) -> T: ...

    def first_true[U](
        self, default: U = None, predicate: Callable[[T], bool] | None = None
    ) -> U | T:
        """
        Returns the first true value in the iterable.

        If no true value is found, returns default

        If pred is not None, returns the first item for which pred(item) == True .
        >>> import pychain as pc
        >>> def gt_five(x: int) -> bool:
        ...     return x > 5
        >>>
        >>> def gt_nine(x: int) -> bool:
        ...     return x > 9
        >>>
        >>> pc.Iter.from_(range(10)).first_true()
        1
        >>> pc.Iter.from_(range(10)).first_true(predicate=gt_five)
        6
        >>> pc.Iter.from_(range(10)).first_true(default="missing", predicate=gt_nine)
        'missing'
        """
        return self.into(mit.first_true, default, predicate)
