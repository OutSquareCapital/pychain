from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz
import more_itertools as mit

from .._core import CommonBase, IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class IterFilter[T](IterWrapper[T]):
    def filter[**P](self, func: Callable[[T], bool]) -> Self:
        """
        Filter elements according to func and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).into(list)
            [2, 3]
        """
        return self._new(partial(filter, func))

    def filter_isin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are in the given values iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4]).filter_isin([2, 4, 6]).into(list)
            [2, 4]
        """
        value_set: set[T] = set(values)
        return self._new(lambda data: (x for x in data if x in value_set))

    def filter_notin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are not in the given values iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4]).filter_notin([2, 4, 6]).into(list)
            [1, 3]
        """
        value_set: set[T] = set(values)
        return self._new(lambda data: (x for x in data if x not in value_set))

    def filter_contain[U: CommonBase[Iterable[str]]](self: U, text: str) -> U:
        """
        Return elements that contain the given text.

            >>> from pychain import Iter
            >>> Iter(["apple", "banana", "cherry", "date"]).filter_contain("ana").into(
            ...     list
            ... )
            ['banana']
        """
        return self._new(lambda data: (x for x in data if text in x))

    def filter_subclass[U: Iterable[type], R](
        self: CommonBase[U], parent: type[R]
    ) -> Iter[type[R]]:
        """
        Return elements that are subclasses of the given class.

            >>> from pychain import Iter
            >>> class A:
            ...     pass
            >>> class B(A):
            ...     pass
            >>> class C:
            ...     pass
            >>> Iter([A, B, C]).filter_subclass(A).map(lambda c: c.__name__).into(list)
            ['A', 'B']
        """
        return self.pipe_into(lambda data: (x for x in data if issubclass(x, parent)))

    def filter_type[R](self, typ: type[R]) -> Iter[R]:
        """
        Return elements that are instances of the given type.

            >>> from pychain import Iter
            >>> Iter([1, "two", 3.0, "four", 5]).filter_type(int).into(list)
            [1, 5]
        """
        return self.pipe_into(lambda data: (x for x in data if isinstance(x, typ)))

    def filter_attr(self, attr: str) -> Self:
        """
        Return elements that have the given attribute.

            >>> from pychain import Iter
            >>> Iter(["hello", "world", 2, 5]).filter_attr("capitalize").into(list)
            ['hello', 'world']
        """
        return self._new(lambda data: (x for x in data if hasattr(x, attr)))

    def filter_callable(self) -> Iter[Callable[..., Any]]:
        """
        Return only elements that are callable.

        >>> from pychain import Iter
        >>> Iter([len, 42, str, None, list]).filter_callable().into(list)
        [<built-in function len>, <class 'str'>, <class 'list'>]
        """
        return self.pipe_into(lambda data: (x for x in data if callable(x)))

    def filter_false(self, func: Callable[[T], bool]) -> Self:
        """
        Return elements for which func is false.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter_false(lambda x: x > 1).into(list)
            [1]
        """
        return self._new(partial(itertools.filterfalse, func))

    def filter_except(
        self, func: Callable[[T], object], *exceptions: type[BaseException]
    ) -> Self:
        """
        Yield the items from iterable for which the validator function does not raise one of the specified exceptions.

        Validator is called for each item in iterable.

        It should be a function that accepts one argument and raises an exception if that item is not valid.

        If an exception other than one given by exceptions is raised by validator, it is raised like normal.

            >>> from pychain import Iter
            >>> iterable = ["1", "2", "three", "4", None]
            >>> Iter(iterable).filter_except(int, ValueError, TypeError).into(list)
            ['1', '2', '4']
        """
        return self._new(lambda data: mit.filter_except(func, data, *exceptions))

    def take_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Take items while predicate holds and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).into(list)
            [1, 2]
        """
        return self._new(partial(itertools.takewhile, predicate))

    def drop_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Drop items while predicate holds and return the remainder.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).into(list)
            [0]
        """
        return self._new(partial(itertools.dropwhile, predicate))

    def compress(self, *selectors: bool) -> Self:
        """
        Filter elements using a boolean selector iterable.

            >>> from pychain import Iter
            >>> Iter("ABCDEF").compress(1, 0, 1, 0, 1, 1).into(list)
            ['A', 'C', 'E', 'F']
        """
        return self._new(itertools.compress, selectors)

    def unique(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return only unique elements of a sequence

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).unique().into(tuple)
        (1, 2, 3)
        >>> Iter([1, 2, 1, 3]).unique().into(tuple)
        (1, 2, 3)

        Uniqueness can be defined by key keyword

        >>> Iter(["cat", "mouse", "dog", "hen"]).unique(key=len).into(tuple)
        ('cat', 'mouse')
        """
        return self._new(cz.itertoolz.unique, key=key)

    def head(self, n: int) -> Self:
        """
        Return first n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).head(2).into(list)
            [1, 2]
        """

        return self._new(partial(cz.itertoolz.take, n))

    def tail(self, n: int) -> Self:
        """
        Return last n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).tail(2).into(list)
            [2, 3]
        """
        return self._new(partial(cz.itertoolz.tail, n))

    def drop_first(self, n: int) -> Self:
        """
        Drop first n elements and return the remainder wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).drop_first(1).into(list)
            [2, 3]
        """
        return self._new(partial(cz.itertoolz.drop, n))

    def unique_justseen(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yields elements in order, ignoring serial duplicates

        >>> from pychain import Iter
        >>> Iter("AAAABBBCCDAABBB").unique_justseen().into(list)
        ['A', 'B', 'C', 'D', 'A', 'B']
        >>> Iter("ABBCcAD").unique_justseen(str.lower).into(list)
        ['A', 'B', 'C', 'A', 'D']
        """
        return self._new(mit.unique_justseen, key=key)

    def unique_in_window(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yield the items from iterable that haven't been seen recently. n is the size of the lookback window.

        >>> from pychain import Iter
        >>> iterable = [0, 1, 0, 2, 3, 0]
        >>> n = 3
        >>> Iter(iterable).unique_in_window(n).into(list)
        [0, 1, 2, 3, 0]

        The key function, if provided, will be used to determine uniqueness:

        >>> Iter("abAcda").unique_in_window(3, key=str.lower).into(list)
        ['a', 'b', 'c', 'd', 'a']

        The items in iterable must be hashable.
        """
        return self._new(mit.unique_in_window, n, key=key)

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return the top-n items according to key.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).top_n(2).into(list)
            [3, 2]
        """
        return self._new(partial(cz.itertoolz.topk, n, key=key))

    def extract(self, indices: Iterable[int]) -> Self:
        """
        Yield values at the specified indices.

        >>> from pychain import Iter
        >>> Iter("abcdefghijklmnopqrstuvwxyz").extract([7, 4, 11, 11, 14]).into(list)
        ['h', 'e', 'l', 'l', 'o']

        The iterable is consumed lazily and can be infinite.

        The indices are consumed immediately and must be finite.

        Raises IndexError if an index lies beyond the iterable.

        Raises ValueError for negative indices.
        """
        return self._new(mit.extract, indices)

    def every(self, index: int) -> Self:
        """
        Return every nth item starting from first.

            >>> from pychain import Iter
            >>> Iter([10, 20, 30, 40]).every(2).into(list)
            [10, 30]
        """
        return self._new(partial(cz.itertoolz.take_nth, index))

    def slice(self, start: int | None = None, stop: int | None = None) -> Self:
        """
        Return a slice of the iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4, 5]).slice(1, 4).into(list)
            [2, 3, 4]
        """
        return self._new(lambda data: itertools.islice(data, start, stop))

    def filter_map[R](self, func: Callable[[T], R]) -> Iter[R]:
        """
        Apply func to every element of iterable, yielding only those which are not None.

        >>> from pychain import Iter
        >>> elems = ["1", "a", "2", "b", "3"]
        >>> Iter(elems).filter_map(lambda s: int(s) if s.isnumeric() else None).into(
        ...     list
        ... )
        [1, 2, 3]
        """
        return self.pipe_into(partial(mit.filter_map, func))
