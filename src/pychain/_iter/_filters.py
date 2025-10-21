from __future__ import annotations

import itertools
from collections.abc import Callable, Generator, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Self, TypeGuard

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class BaseFilter[T](IterWrapper[T]):
    def filter(self, func: Callable[[T], bool]) -> Self:
        """
        Return an iterator yielding those items of iterable for which function is true.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).filter(lambda x: x > 1).into(list)
        [2, 3]
        """
        return self._new(partial(filter, func))

    def filter_isin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are in the given values iterable.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3, 4]).filter_isin([2, 4, 6]).into(list)
        [2, 4]
        """
        value_set: set[T] = set(values)
        return self._new(lambda data: (x for x in data if x in value_set))

    def filter_notin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are not in the given values iterable.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3, 4]).filter_notin([2, 4, 6]).into(list)
        [1, 3]
        """
        value_set: set[T] = set(values)
        return self._new(lambda data: (x for x in data if x not in value_set))

    def filter_contain[U: IterWrapper[str]](
        self: U, text: str, format: Callable[[str], str] | None = None
    ) -> U:
        """
        Return elements that contain the given text.

        Optionally, a format function can be provided to preprocess each element before checking for the substring.
        >>> import pychain as pc
        >>>
        >>> data = pc.Iter(["apple", "banana", "cherry", "date"])
        >>> data.filter_contain("ana").into(list)
        ['banana']
        >>> upper_data = data.map(str.upper).apply(list)
        >>> upper_data.filter_contain("an").into(list)
        []
        >>> upper_data.filter_contain("ana", str.lower).into(list)
        ['BANANA']
        """

        def _(x: str) -> bool:
            formatted = format(x) if format else x
            return text in formatted

        return self._new(lambda data: (x for x in data if _(x)))

    def filter_attr[U](self, attr: str, dtype: type[U] = object) -> Iter[U]:
        """
        Return elements that have the given attribute.

        Optionally, specify the expected type of the attribute for better type hinting.

        This does not enforce type checking at runtime for performance considerations.
        >>> import pychain as pc
        >>> pc.Iter(["hello", "world", 2, 5]).filter_attr("capitalize", str).into(list)
        ['hello', 'world']
        """

        def check(data: Iterable[Any]) -> Generator[U, None, None]:
            def _(x: Any) -> TypeGuard[U]:
                return hasattr(x, attr)

            return (x for x in data if _(x))

        return self.apply(check)

    def filter_false(self, func: Callable[[T], bool]) -> Self:
        """
        Return elements for which func is false.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).filter_false(lambda x: x > 1).into(list)
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
        >>> import pychain as pc
        >>> iterable = ["1", "2", "three", "4", None]
        >>> pc.Iter(iterable).filter_except(int, ValueError, TypeError).into(list)
        ['1', '2', '4']
        """
        return self._new(lambda data: mit.filter_except(func, data, *exceptions))

    def take_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Take items while predicate holds and return a new Iterable wrapper.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 0]).take_while(lambda x: x > 0).into(list)
        [1, 2]
        """
        return self._new(partial(itertools.takewhile, predicate))

    def drop_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Drop items while predicate holds and return the remainder.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 0]).drop_while(lambda x: x > 0).into(list)
        [0]
        """
        return self._new(partial(itertools.dropwhile, predicate))

    def compress(self, *selectors: bool) -> Self:
        """
        Filter elements using a boolean selector iterable.
        >>> import pychain as pc
        >>> pc.Iter("ABCDEF").compress(1, 0, 1, 0, 1, 1).into(list)
        ['A', 'C', 'E', 'F']
        """
        return self._new(itertools.compress, selectors)

    def unique(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return only unique elements of a sequence
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).unique().into(tuple)
        (1, 2, 3)
        >>> pc.Iter([1, 2, 1, 3]).unique().into(tuple)
        (1, 2, 3)

        Uniqueness can be defined by key keyword
        >>> pc.Iter(["cat", "mouse", "dog", "hen"]).unique(key=len).into(tuple)
        ('cat', 'mouse')
        """
        return self._new(cz.itertoolz.unique, key=key)

    def head(self, n: int) -> Self:
        """
        Return first n elements wrapped.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).head(2).into(list)
        [1, 2]
        """

        return self._new(partial(cz.itertoolz.take, n))

    def tail(self, n: int) -> Self:
        """
        Return last n elements wrapped.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).tail(2).into(list)
        [2, 3]
        """
        return self._new(partial(cz.itertoolz.tail, n))

    def drop_first(self, n: int) -> Self:
        """
        Drop first n elements and return the remainder wrapped.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).drop_first(1).into(list)
        [2, 3]
        """
        return self._new(partial(cz.itertoolz.drop, n))

    def unique_justseen(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yields elements in order, ignoring serial duplicates

        >>> import pychain as pc
        >>> pc.Iter("AAAABBBCCDAABBB").unique_justseen().into(list)
        ['A', 'B', 'C', 'D', 'A', 'B']
        >>> pc.Iter("ABBCcAD").unique_justseen(str.lower).into(list)
        ['A', 'B', 'C', 'A', 'D']
        """
        return self._new(mit.unique_justseen, key=key)

    def unique_in_window(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yield the items from iterable that haven't been seen recently. n is the size of the lookback window.
        >>> import pychain as pc
        >>> iterable = [0, 1, 0, 2, 3, 0]
        >>> n = 3
        >>> pc.Iter(iterable).unique_in_window(n).into(list)
        [0, 1, 2, 3, 0]

        The key function, if provided, will be used to determine uniqueness:
        >>> pc.Iter("abAcda").unique_in_window(3, key=str.lower).into(list)
        ['a', 'b', 'c', 'd', 'a']

        The items in iterable must be hashable.
        """
        return self._new(mit.unique_in_window, n, key=key)

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return the top-n items according to key.
        >>> import pychain as pc
        >>> pc.Iter([1, 3, 2]).top_n(2).into(list)
        [3, 2]
        """
        return self._new(partial(cz.itertoolz.topk, n, key=key))

    def extract(self, indices: Iterable[int]) -> Self:
        """
        Yield values at the specified indices.
        >>> import pychain as pc
        >>> pc.Iter("abcdefghijklmnopqrstuvwxyz").extract([7, 4, 11, 11, 14]).into(list)
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
        >>> import pychain as pc
        >>> pc.Iter([10, 20, 30, 40]).every(2).into(list)
        [10, 30]
        """
        return self._new(partial(cz.itertoolz.take_nth, index))

    def slice(self, start: int | None = None, stop: int | None = None) -> Self:
        """
        Return a slice of the iterable.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3, 4, 5]).slice(1, 4).into(list)
        [2, 3, 4]
        """
        return self._new(lambda data: itertools.islice(data, start, stop))

    def filter_subclass[U: type[Any], R](
        self: IterWrapper[U], parent: type[R], keep_parent: bool = True
    ) -> Iter[type[R]]:
        """
        Return elements that are subclasses of the given class, optionally excluding the parent class itself.
        >>> import pychain as pc
        >>> class A:
        ...     pass
        >>> class B(A):
        ...     pass
        >>> class C:
        ...     pass
        >>> def name(cls: type[Any]) -> str:
        ...     return cls.__name__
        >>>
        >>> data = pc.Iter([A, B, C])
        >>> data.filter_subclass(A).map(name).into(list)
        ['A', 'B']
        >>> data.filter_subclass(A, keep_parent=False).map(name).into(list)
        ['B']
        """

        def _(data: Iterable[type[Any]]) -> Generator[type[R], None, None]:
            if keep_parent:
                return (x for x in data if issubclass(x, parent))
            else:
                return (x for x in data if issubclass(x, parent) and x is not parent)

        return self.apply(_)

    def filter_type[R](self, typ: type[R]) -> Iter[R]:
        """
        Return elements that are instances of the given type.
        >>> import pychain as pc
        >>> pc.Iter([1, "two", 3.0, "four", 5]).filter_type(int).into(list)
        [1, 5]
        """
        return self.apply(lambda data: (x for x in data if isinstance(x, typ)))

    def filter_callable(self) -> Iter[Callable[..., Any]]:
        """
        Return only elements that are callable.
        >>> import pychain as pc
        >>> pc.Iter([len, 42, str, None, list]).filter_callable().into(list)
        [<built-in function len>, <class 'str'>, <class 'list'>]
        """
        return self.apply(lambda data: (x for x in data if callable(x)))

    def filter_map[R](self, func: Callable[[T], R]) -> Iter[R]:
        """
        Apply func to every element of iterable, yielding only those which are not None.
        >>> import pychain as pc
        >>>
        >>> def to_int(s: str) -> int | None:
        ...     return int(s) if s.isnumeric() else None
        >>> elems = ["1", "a", "2", "b", "3"]
        >>> pc.Iter(elems).filter_map(to_int).into(list)
        [1, 2, 3]
        """
        return self.apply(partial(mit.filter_map, func))
