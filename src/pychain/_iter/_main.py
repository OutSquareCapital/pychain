from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Concatenate, overload

import cytoolz as cz
import more_itertools as mit

from .._core import dict_factory
from .._protocols import Pluckable, SupportsRichComparison
from ._aggregations import IterAgg
from ._maps import IterMap
from ._process import IterProcess
from ._rolling import IterRolling
from ._struct import StructNameSpace
from ._tuples import IterTuples

if TYPE_CHECKING:
    from .._dict import Dict


class Iter[T](IterAgg[T], IterProcess[T], IterTuples[T], IterRolling[T], IterMap[T]):
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
        >>> data.pluck("val").to_list()
        ['a', 'b']
        >>> Iter([[10, 20], [30, 40]]).pluck(0).to_list()
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

        >>> Iter([1, 2]).repeat(2).to_list()
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

        >>> Iter(range(3)).repeat_last().head(5).to_list()
        [0, 1, 2, 2, 2]

        If the iterable is empty, yield default forever:

        >>> Iter(range(0)).repeat_last(42).head(5).to_list()
        [42, 42, 42, 42, 42]
        """
        return Iter(mit.repeat_last(self._data, default))

    def flatten[U](self: Iter[Iterable[U]]) -> Iter[U]:
        """
        Flatten one level of nesting and return a new Iterable wrapper.

        >>> Iter([[1, 2], [3]]).flatten().to_list()
        [1, 2, 3]
        """
        return Iter(itertools.chain.from_iterable(self._data))

    def split_at(
        self,
        pred: Callable[[T], bool],
        maxsplit: int = -1,
        keep_separator: bool = False,
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list is delimited by an item where callable pred returns True.

        >>> Iter("abcdcba").split_at(lambda x: x == "b").to_list()
        [['a'], ['c', 'd', 'c'], ['a']]
        >>> Iter(range(10)).split_at(lambda n: n % 2 == 1).to_list()
        [[0], [2], [4], [6], [8], []]

        At most *maxsplit* splits are done.

        If *maxsplit* is not specified or -1, then there is no limit on the number of splits:

        >>> Iter(range(10)).split_at(lambda n: n % 2 == 1, maxsplit=2).to_list()
        [[0], [2], [4, 5, 6, 7, 8, 9]]

        By default, the delimiting items are not included in the output.

        To include them, set *keep_separator* to `True`.

        >>> Iter("abcdcba").split_at(lambda x: x == "b", keep_separator=True).to_list()
        [['a'], ['b'], ['c', 'd', 'c'], ['b'], ['a']]
        """
        return Iter(mit.split_at(self._data, pred, maxsplit, keep_separator))

    def split_after(
        self, predicate: Callable[[T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list ends with an item where callable pred returns True:
        At most maxsplit splits are done.
        If maxsplit is not specified or -1, then there is no limit on the number of splits:

        >>> Iter("one1two2").split_after(str.isdigit).to_list()
        [['o', 'n', 'e', '1'], ['t', 'w', 'o', '2']]

        >>> Iter(range(10)).split_after(lambda n: n % 3 == 0).to_list()
        [[0], [1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> Iter(range(10)).split_after(lambda n: n % 3 == 0, max_split=2).to_list()
        [[0], [1, 2, 3], [4, 5, 6, 7, 8, 9]]
        """
        return Iter(mit.split_after(self._data, predicate, max_split))

    def split_before(
        self, predicate: Callable[[T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list ends with an item where callable pred returns True.

        >>> Iter("abcdcba").split_before(lambda x: x == "b").to_list()
        [['a'], ['b', 'c', 'd', 'c'], ['b', 'a']]
        >>> Iter(range(10)).split_before(lambda n: n % 2 == 1).to_list()
        [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]]

        At most *max_split* splits are done.

        If *max_split* is not specified or -1, then there is no limit on the number of splits:

        >>> Iter(range(10)).split_before(lambda n: n % 2 == 1, max_split=2).to_list()
        [[0], [1, 2], [3, 4, 5, 6, 7, 8, 9]]
        """
        return Iter(mit.split_before(self._data, predicate, max_split))

    def split_into(self, sizes: Iterable[int | None]) -> Iter[list[T]]:
        """
        Yield a list of sequential items from iterable of length 'n' for each integer 'n' in sizes.

        >>> Iter([1, 2, 3, 4, 5, 6]).split_into([1, 2, 3]).to_list()
        [[1], [2, 3], [4, 5, 6]]

        If the sum of sizes is smaller than the length of iterable, then the remaining items of iterable will not be returned.

        >>> Iter([1, 2, 3, 4, 5, 6]).split_into([2, 3]).to_list()
        [[1, 2], [3, 4, 5]]

        If the sum of sizes is larger than the length of iterable, fewer items will be returned in the iteration that overruns the iterable and further lists will be empty:

        >>> Iter([1, 2, 3, 4]).split_into([1, 2, 3, 4]).to_list()
        [[1], [2, 3], [4], []]

        When a None object is encountered in sizes, the returned list will contain items up to the end of iterable the same way that itertools.slice does:

        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]).split_into([2, 3, None]).to_list()
        [[1, 2], [3, 4, 5], [6, 7, 8, 9, 0]]

        split_into can be useful for grouping a series of items where the sizes of the groups are not uniform.

        An example would be where in a row from a table, multiple columns represent elements of the same feature (e.g. a point represented by x,y,z) but, the format is not the same for all columns.
        """
        return Iter(mit.split_into(self._data, sizes))

    def split_when(
        self, predicate: Callable[[T, T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Split iterable into pieces based on the output of pred. pred should be a function that takes successive pairs of items and returns True if the iterable should be split in between them.

        For example, to find runs of increasing numbers, split the iterable when element i is larger than element i + 1:

        >>> Iter([1, 2, 3, 3, 2, 5, 2, 4, 2]).split_when(lambda x, y: x > y).to_list()
        [[1, 2, 3, 3], [2, 5], [2, 4], [2]]

        At most max_split splits are done.

        If max_split is not specified or -1, then there is no limit on the number of splits:

        >>> Iter([1, 2, 3, 3, 2, 5, 2, 4, 2]).split_when(
        ...     lambda x, y: x > y, max_split=2
        ... ).to_list()
        [[1, 2, 3, 3], [2, 5], [2, 4, 2]]
        """
        return Iter(mit.split_when(self._data, predicate, max_split))

    def chunked(self, n: int, strict: bool = False) -> Iter[list[T]]:
        """
        Break iterable into lists of length n.

        By default, the last yielded list will have fewer than *n* elements if the length of *iterable* is not divisible by *n*.

        To use a fill-in value instead, see the :func:`grouper` recipe.

        If the length of *iterable* is not divisible by *n* and *strict* is
        ``True``, then ``ValueError`` will be raised before the last
        list is yielded.

        >>> Iter([1, 2, 3, 4, 5, 6]).chunked(3).to_list()
        [[1, 2, 3], [4, 5, 6]]
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).chunked(3).to_list()
        [[1, 2, 3], [4, 5, 6], [7, 8]]
        """
        return Iter(mit.chunked(self._data, n, strict))

    def ichunked(self, n: int) -> Iter[Iterator[T]]:
        """

        Break *iterable* into sub-iterables with *n* elements each.

        :func:`ichunked` is like :func:`chunked`, but it yields iterables
        instead of lists.

        If the sub-iterables are read in order, the elements of *iterable*
        won't be stored in memory.

        If they are read out of order, :func:`itertools.tee` is used to cache
        elements as necessary.

        >>> from pychain import iter_count
        >>> all_chunks = iter_count().ichunked(4).unwrap()
        >>> c_1, c_2, c_3 = next(all_chunks), next(all_chunks), next(all_chunks)
        >>> list(c_2)  # c_1's elements have been cached; c_3's haven't been
        [4, 5, 6, 7]
        >>> list(c_1)
        [0, 1, 2, 3]
        >>> list(c_3)
        [8, 9, 10, 11]
        """
        return Iter(mit.ichunked(self._data, n))

    def chunked_even(self, n: int) -> Iter[list[T]]:
        """
        Break iterable into lists of approximately length n.
        Items are distributed such the lengths of the lists differ by at most 1 item.

        >>> iterable = [1, 2, 3, 4, 5, 6, 7]
        >>> Iter(iterable).chunked_even(3).to_list()  # List lengths: 3, 2, 2
        [[1, 2, 3], [4, 5], [6, 7]]
        >>> Iter(iterable).chunked(3).to_list()  # List lengths: 3, 3, 1
        [[1, 2, 3], [4, 5, 6], [7]]
        """
        return Iter(mit.chunked_even(self._data, n))

    def sort[U: SupportsRichComparison[Any]](
        self: Iter[U],
        key: Callable[[U], Any] | None = None,
        reverse: bool = False,
    ) -> Iter[U]:
        """Sort the elements of the sequence.
        Note: This method must consume the entire iterable to perform the sort.
        The result is a new iterable over the sorted sequence.

        >>> Iter([3, 1, 2]).sort().to_list()
        [1, 2, 3]
        >>> data = Iter([{"age": 30}, {"age": 20}])
        >>> data.sort(key=lambda x: x["age"]).to_list()
        [{'age': 20}, {'age': 30}]
        """
        return self._new(sorted(self._data, key=key, reverse=reverse))

    def group_by[K](self, on: Callable[[T], K]) -> Dict[K, list[T]]:
        """
        Group elements by key function and return a Dict result.

        >>> names = [
        ...     "Alice",
        ...     "Bob",
        ...     "Charlie",
        ...     "Dan",
        ...     "Edith",
        ...     "Frank",
        ... ]
        >>> Iter(names).group_by(len).sort()
        {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

        Non-callable keys imply grouping on a member.

        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        {'F': [{'name': 'Alice', 'gender': 'F'}], 'M': [{'name': 'Bob', 'gender': 'M'}, {'name': 'Charlie', 'gender': 'M'}]}
        """
        return dict_factory(cz.itertoolz.groupby(on, self._data))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.

        >>> Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        return dict_factory(cz.itertoolz.frequencies(self._data))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function

        >>> Iter(["cat", "mouse", "dog"]).count_by(len)
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> Iter([1, 2, 3]).count_by(iseven)
        {False: 2, True: 1}
        """
        return dict_factory(cz.recipes.countby(key, self._data))

    def unique_to_each(self, *others: Iterable[T]) -> Iter[list[T]]:
        """
        Return the elements from each of the input iterables that aren't in the other input iterables.

        For example, suppose you have a set of packages, each with a set of dependencies:

        **{'pkg_1': {'A', 'B'}, 'pkg_2': {'B', 'C'}, 'pkg_3': {'B', 'D'}}**

        If you remove one package, which dependencies can also be removed?

        If pkg_1 is removed, then A is no longer necessary - it is not associated with pkg_2 or pkg_3.

        Similarly, C is only needed for pkg_2, and D is only needed for pkg_3:

        >>> Iter({"A", "B"}).unique_to_each({"B", "C"}, {"B", "D"}).to_list()
        [['A'], ['C'], ['D']]

        If there are duplicates in one input iterable that aren't in the others they will be duplicated in the output.

        Input order is preserved:

        >>> Iter("mississippi").unique_to_each("missouri").to_list()
        [['p', 'p'], ['o', 'u', 'r']]

        It is assumed that the elements of each iterable are hashable.
        """
        return Iter(mit.unique_to_each(self._data, *others))

    def partition_by(self, predicate: Callable[[T], bool]) -> Iter[tuple[T, ...]]:
        """
        Partition the `iterable` into a sequence of `tuples` according to a predicate function.

        Every time the output of `predicate` changes, a new `tuple` is started,
        and subsequent items are collected into that `tuple`.

        >>> Iter("I have space").partition_by(lambda c: c == " ").to_list()
        [('I',), (' ',), ('h', 'a', 'v', 'e'), (' ',), ('s', 'p', 'a', 'c', 'e')]

        >>> data = [1, 2, 1, 99, 88, 33, 99, -1, 5]
        >>> Iter(data).partition_by(lambda x: x > 10).to_list()
        [(1, 2, 1), (99, 88, 33, 99), (-1, 5)]

        """
        return Iter(cz.recipes.partitionby(predicate, self._data))
