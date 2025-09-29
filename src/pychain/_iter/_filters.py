from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, Self

import cytoolz as cz
import more_itertools as mit

from .._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._main import Iter


class IterFilter[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """
        Filter elements according to func and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).to_list()
            [2, 3]
        """
        return self._new(filter(func, self._data, *args, **kwargs))

    def filter_isin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are in the given values iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4]).filter_isin([2, 4, 6]).to_list()
            [2, 4]
        """
        value_set: set[T] = set(values)
        return self._new((x for x in self._data if x in value_set))

    def filter_notin(self, values: Iterable[T]) -> Self:
        """
        Return elements that are not in the given values iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4]).filter_notin([2, 4, 6]).to_list()
            [1, 3]
        """
        value_set: set[T] = set(values)
        return self._new((x for x in self._data if x not in value_set))

    def filter_contain[U: CommonBase[Iterable[str]]](self: U, text: str) -> U:
        """
        Return elements that contain the given text.

            >>> from pychain import Iter
            >>> Iter(["apple", "banana", "cherry", "date"]).filter_contain(
            ...     "ana"
            ... ).to_list()
            ['banana']
        """
        return self._new((x for x in self._data if text in x))

    def filter_type[R](self, typ: type[R]) -> Iter[R]:
        """
        Return elements that are instances of the given type.

            >>> from pychain import Iter
            >>> Iter([1, "two", 3.0, "four", 5]).filter_type(int).to_list()
            [1, 5]
        """
        return iter_factory((x for x in self._data if isinstance(x, typ)))

    def filter_attr(self, attr: str) -> Self:
        """
        Return elements that have the given attribute.

            >>> from pychain import Iter
            >>> Iter(["hello", "world", 2, 5]).filter_attr("capitalize").to_list()
            ['hello', 'world']
        """
        return self._new((x for x in self._data if hasattr(x, attr)))

    def filter_false[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """
        Return elements for which func is false.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter_false(lambda x: x > 1).to_list()
            [1]
        """
        return self._new(itertools.filterfalse(func, self._data, *args, **kwargs))

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
            >>> Iter(iterable).filter_except(int, ValueError, TypeError).to_list()
            ['1', '2', '4']
        """
        return self._new(mit.filter_except(func, self._data, *exceptions))

    def take_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Take items while predicate holds and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).to_list()
            [1, 2]
        """
        return self._new(itertools.takewhile(predicate, self._data))

    def drop_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Drop items while predicate holds and return the remainder.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).to_list()
            [0]
        """
        return self._new(itertools.dropwhile(predicate, self._data))

    def compress(self, *selectors: bool) -> Self:
        """
        Filter elements using a boolean selector iterable.

            >>> from pychain import Iter
            >>> Iter("ABCDEF").compress(1, 0, 1, 0, 1, 1).to_list()
            ['A', 'C', 'E', 'F']
        """
        return self._new(itertools.compress(self._data, selectors))

    def unique(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return only unique elements of a sequence

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).unique().pipe_unwrap(tuple)
        (1, 2, 3)
        >>> Iter([1, 2, 1, 3]).unique().pipe_unwrap(tuple)
        (1, 2, 3)

        Uniqueness can be defined by key keyword

        >>> Iter(["cat", "mouse", "dog", "hen"]).unique(key=len).pipe_unwrap(tuple)
        ('cat', 'mouse')
        """
        return self._new(cz.itertoolz.unique(self._data, key=key))

    def head(self, n: int) -> Self:
        """
        Return first n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).head(2).to_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        """
        Return last n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).tail(2).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        """
        Drop first n elements and return the remainder wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).drop_first(1).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.drop(n, self._data))

    def unique_justseen(self, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yields elements in order, ignoring serial duplicates

        >>> from pychain import Iter
        >>> Iter("AAAABBBCCDAABBB").unique_justseen().to_list()
        ['A', 'B', 'C', 'D', 'A', 'B']
        >>> Iter("ABBCcAD").unique_justseen(str.lower).to_list()
        ['A', 'B', 'C', 'A', 'D']
        """
        return self._new(mit.unique_justseen(self._data, key=key))

    def unique_in_window(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Yield the items from iterable that haven't been seen recently. n is the size of the lookback window.

        >>> from pychain import Iter
        >>> iterable = [0, 1, 0, 2, 3, 0]
        >>> n = 3
        >>> Iter(iterable).unique_in_window(n).to_list()
        [0, 1, 2, 3, 0]

        The key function, if provided, will be used to determine uniqueness:

        >>> Iter("abAcda").unique_in_window(3, key=str.lower).to_list()
        ['a', 'b', 'c', 'd', 'a']

        The items in iterable must be hashable.
        """
        return self._new(mit.unique_in_window(self._data, n, key=key))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return the top-n items according to key.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).top_n(2).to_list()
            [3, 2]
        """
        return self._new(cz.itertoolz.topk(n, self._data, key))

    def extract(self, indices: Iterable[int]) -> Self:
        """
        Yield values at the specified indices.

        >>> from pychain import Iter
        >>> Iter("abcdefghijklmnopqrstuvwxyz").extract([7, 4, 11, 11, 14]).to_list()
        ['h', 'e', 'l', 'l', 'o']

        The iterable is consumed lazily and can be infinite.

        The indices are consumed immediately and must be finite.

        Raises IndexError if an index lies beyond the iterable.

        Raises ValueError for negative indices.
        """
        return self._new(mit.extract(self._data, indices))

    def every(self, index: int) -> Self:
        """
        Return every nth item starting from first.

            >>> from pychain import Iter
            >>> Iter([10, 20, 30, 40]).every(2).to_list()
            [10, 30]
        """
        return self._new(cz.itertoolz.take_nth(index, self._data))

    def slice(self, start: int | None = None, stop: int | None = None) -> Self:
        """
        Return a slice of the iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4, 5]).slice(1, 4).to_list()
            [2, 3, 4]
        """
        return self._new(itertools.islice(self._data, start, stop))
