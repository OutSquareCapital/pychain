from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import Any, Concatenate, overload

import cytoolz as cz
import more_itertools as mit

from .._protocols import Pluckable, SupportsRichComparison
from ._aggregations import IterAgg
from ._booleans import IterBool
from ._constructors import IterConstructors
from ._dicts import IterDicts
from ._filters import IterFilter
from ._lists import IterList
from ._maps import IterMap
from ._process import IterProcess
from ._rolling import IterRolling
from ._struct import StructNameSpace
from ._tuples import IterTuples


class Iter[T](
    IterAgg[T],
    IterProcess[T],
    IterTuples[T],
    IterBool[T],
    IterRolling[T],
    IterMap[T],
    IterDicts[T],
    IterList[T],
    IterFilter[T],
    IterConstructors,
):
    """
    A wrapper around Python's built-in iterable types, providing a rich set of functional programming tools.

    It supports lazy evaluation, allowing for efficient processing of large datasets.

    It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

    It can be constructed from any iterable, including `lists`, `tuples`, `sets`, and `generators`.
    """

    _data: Iterable[T]
    __slots__ = ("_data",)

    def pipe_into[**P, R](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to the underlying iterable and return a new Iter.

        >>> from pychain import Iter
        >>> from collections.abc import Iterable
        >>>
        >>> def double_values(iterable: Iterable[int]) -> Iterable[int]:
        ...     return (i * 2 for i in iterable)
        >>>
        >>> Iter(range(5)).pipe_into(double_values).into(list)
        [0, 2, 4, 6, 8]
        """
        return Iter(func(self._data, *args, **kwargs))

    @property
    def struct[K, V](self: Iter[dict[K, V]]) -> StructNameSpace[K, V]:
        """
        A namespace for dictionary-specific methods.

        Expose the same functionality as Dict, but in a way that works on an iterable of dicts, with generators under the hood.
        """
        return StructNameSpace(self._data)

    def pluck[K, V](self: Iter[Pluckable[K, V]], key: K) -> Iter[V]:
        """
        Extract a value from each element in the sequence using a key or index.
        This is a shortcut for `.map(lambda x: x[key])`.

        >>> data = Iter([{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
        >>> data.pluck("val").into(list)
        ['a', 'b']
        >>> Iter([[10, 20], [30, 40]]).pluck(0).into(list)
        [10, 30]
        """
        return Iter(cz.itertoolz.pluck(key, self._data))

    def reduce_by[K](
        self,
        key: Callable[[T], K],
        binop: Callable[[T, T], T],
        init: Any = "__no__default__",
    ) -> Iter[K]:
        """
        Perform a simultaneous groupby and reduction

        >>> data = Iter([1, 2, 3, 4, 5])
        >>> data.reduce_by(lambda x: x % 2 == 0, lambda x, y: x + y, 0)
        {False: 9, True: 6}
        >>> data.group_by(lambda x: x % 2 == 0).map_values(
        ...     lambda group: Iter(group).reduce(lambda x, y: x + y)
        ... )
        {False: 9, True: 6}

        But the former does not build the intermediate groups, allowing it to operate in much less space.

        This makes it suitable for larger datasets that do not fit comfortably in memory

        The init keyword argument is the default initialization of the reduction.

        This can be either a constant value like 0 or a callable like lambda : 0 as might be used in defaultdict.

        Simple Examples

        >>> from operator import add, mul
        >>> Iter([1, 2, 3, 4, 5]).reduce_by(lambda x: x % 2 == 0, add)
        {False: 9, True: 6}
        >>> Iter([1, 2, 3, 4, 5]).reduce_by(lambda x: x % 2 == 0, mul)
        {False: 15, True: 8}

        Complex Example

        >>> projects = [
        ...     {"name": "build roads", "state": "CA", "cost": 1000000},
        ...     {"name": "fight crime", "state": "IL", "cost": 100000},
        ...     {"name": "help farmers", "state": "IL", "cost": 2000000},
        ...     {"name": "help farmers", "state": "CA", "cost": 200000},
        ... ]
        >>> Iter(projects).reduce_by(
        ...     "state",
        ...     lambda acc, x: acc + x["cost"],
        ...     0,
        ... )
        {'CA': 1200000, 'IL': 2100000}

        Example Using init

        >>> def set_add(s, i):
        ...     s.add(i)
        ...     return s
        >>> Iter([1, 2, 3, 4, 1, 2, 3]).reduce_by(lambda x: x % 2 == 0, set_add, set)
        {False: {1, 3}, True: {2, 4}}
        """
        return Iter(cz.itertoolz.reduceby(key, binop, self._data, init))

    def repeat(self, n: int) -> Iter[Iterable[T]]:
        """
        Repeat the entire iterable n times (as elements) and return Iter.

        >>> Iter([1, 2]).repeat(2).into(list)
        [[1, 2], [1, 2]]
        """
        return Iter(itertools.repeat(self._data, n))

    @overload
    def repeat_last(self, default: T) -> Iter[T]: ...
    @overload
    def repeat_last[U](self, default: U) -> Iter[T | U]: ...
    def repeat_last[U](self, default: U = None) -> Iter[T | U]:
        """
        After the iterable is exhausted, keep yielding its last element.

        >>> Iter(range(3)).repeat_last().head(5).into(list)
        [0, 1, 2, 2, 2]

        If the iterable is empty, yield default forever:

        >>> Iter(range(0)).repeat_last(42).head(5).into(list)
        [42, 42, 42, 42, 42]
        """
        return Iter(mit.repeat_last(self._data, default))

    def flatten[U](self: Iter[Iterable[U]]) -> Iter[U]:
        """
        Flatten one level of nesting and return a new Iterable wrapper.

        >>> Iter([[1, 2], [3]]).flatten().into(list)
        [1, 2, 3]
        """
        return Iter(itertools.chain.from_iterable(self._data))

    def ichunked(self, n: int) -> Iter[Iterator[T]]:
        """

        Break *iterable* into sub-iterables with *n* elements each.

        :func:`ichunked` is like :func:`chunked`, but it yields iterables
        instead of lists.

        If the sub-iterables are read in order, the elements of *iterable*
        won't be stored in memory.

        If they are read out of order, :func:`itertools.tee` is used to cache
        elements as necessary.

        >>> from pychain import Iter
        >>> all_chunks = Iter.from_count().ichunked(4).unwrap()
        >>> c_1, c_2, c_3 = next(all_chunks), next(all_chunks), next(all_chunks)
        >>> list(c_2)  # c_1's elements have been cached; c_3's haven't been
        [4, 5, 6, 7]
        >>> list(c_1)
        [0, 1, 2, 3]
        >>> list(c_3)
        [8, 9, 10, 11]
        """
        return Iter(mit.ichunked(self._data, n))

    def sort[U: SupportsRichComparison[Any]](
        self: Iter[U],
        key: Callable[[U], Any] | None = None,
        reverse: bool = False,
    ) -> Iter[U]:
        """Sort the elements of the sequence.
        Note: This method must consume the entire iterable to perform the sort.
        The result is a new iterable over the sorted sequence.

        >>> Iter([3, 1, 2]).sort().into(list)
        [1, 2, 3]
        >>> data = Iter([{"age": 30}, {"age": 20}])
        >>> data.sort(key=lambda x: x["age"]).into(list)
        [{'age': 20}, {'age': 30}]
        """
        return self._new(sorted(self._data, key=key, reverse=reverse))
