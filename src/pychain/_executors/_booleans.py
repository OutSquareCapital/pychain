from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from .._implementations import Expr, Iter


class BaseBool[T](IterWrapper[T]):
    @overload
    def is_iterable(self: Iter[T]) -> bool: ...
    @overload
    def is_iterable(self: Expr) -> Expr: ...
    def is_iterable(self):
        """
        Return True if the iterable is not empty.

        >>> from pychain import Iter
        >>> Iter([1]).is_iterable()
        True
        >>> Iter([]).is_iterable()
        True
        """
        return self.into(cz.itertoolz.isiterable)

    @overload
    def is_distinct(self: Iter[T]) -> bool: ...
    @overload
    def is_distinct(self: Expr) -> Expr: ...
    def is_distinct(self):
        """
        Return True if all items are distinct.

        >>> from pychain import Iter
        >>> Iter([1, 2]).is_distinct()
        True
        """
        return self.into(cz.itertoolz.isdistinct)

    @overload
    def all(self: Iter[T]) -> bool: ...
    @overload
    def all(self: Expr) -> Expr: ...

    def all(self):
        """
        Return True if all items are truthy.

        >>> from pychain import Iter
        >>> Iter([1, True]).all()
        True
        """
        return self.into(all)

    @overload
    def any(self: Iter[T]) -> bool: ...
    @overload
    def any(self: Expr) -> Expr: ...

    def any(self):
        """
        Return True if any item is truthy.

        >>> from pychain import Iter
        >>> Iter([0, 1]).any()
        True
        """
        return self.into(any)

    @overload
    def all_equal[U](self: Iter[T], key: Callable[[T], U] | None = None) -> bool: ...
    @overload
    def all_equal(self: Expr, key: Callable[[Any], Any] | None = None) -> Expr: ...

    def all_equal[U](self, key: Callable[[T], U] | None = None):
        """
        Return True if all items are equal.

        >>> from pychain import Iter
        >>> Iter([1, 1, 1]).all_equal()
        True

        A function that accepts a single argument and returns a transformed version of each input item can be specified with key:

        >>> Iter("AaaA").all_equal(key=str.casefold)
        True
        >>> Iter([1, 2, 3]).all_equal(key=lambda x: x < 10)
        True
        """
        return self.into(mit.all_equal, key=key)

    @overload
    def all_unique[U](self: Iter[T], key: Callable[[T], U] | None = None) -> bool: ...
    @overload
    def all_unique(self: Expr, key: Callable[[Any], Any] | None = None) -> Expr: ...

    def all_unique[U](self, key: Callable[[T], U] | None = None):
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
        return self.into(mit.all_unique, key=key)

    @overload
    def is_sorted[U](
        self: Iter[T],
        key: Callable[[T], U] | None = None,
        reverse: bool = False,
        strict: bool = False,
    ) -> bool: ...
    @overload
    def is_sorted(
        self: Expr,
        key: Callable[[Any], Any] | None = None,
        reverse: bool = False,
        strict: bool = False,
    ) -> Expr: ...
    def is_sorted[U](
        self,
        key: Callable[[T], U] | None = None,
        reverse: bool = False,
        strict: bool = False,
    ):
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
        return self.into(mit.is_sorted, key=key, reverse=reverse, strict=strict)
