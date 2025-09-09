import itertools
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Concatenate, Self

import cytoolz as cz

from ._core import CommonBase, Process, Transform, flatten_recursive
from ._dict import BaseDict
from ._iter import BaseIter
from ._list import BaseList


@dataclass(slots=True)
class Iter[T](BaseIter[T], CommonBase[Iterable[T]]):
    """
    Public eager Iter wrapper providing chainable iterable operations.

    Use this class for examples and interactive transformations. Methods
    return Iter instances wrapping the underlying Python iterable.
    """

    def pipe[U, **P](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Apply func to the internal iterable and wrap the result in Iter.

        Example:
            >>> Iter([1, 2]).pipe(lambda lst: [x * 2 for x in lst]).into_list().unwrap()
            [2, 4]
        """
        return Iter(func(self._data, *args, **kwargs))

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ):
        """Map each element through func and return a Iter of results.

        Example:
            >>> Iter([1, 2]).map(lambda x: x + 1).into_list().unwrap()
            [2, 3]
        """
        return Iter(map(func, self._data, *args, **kwargs))

    def flat_map[R, **P](
        self,
        func: Callable[Concatenate[T, P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Apply func producing iterables and flatten the results into a Iter.

        Example:
            >>> Iter([1, 2]).flat_map(lambda x: [x, -x]).into_list().unwrap()
            [1, -1, 2, -2]
        """
        return Iter(cz.itertoolz.concat(map(func, self._data, *args, **kwargs)))

    def enumerate(self):
        """Return a Iter of (index, value) pairs.

        Example:
            >>> Iter(["a", "b"]).enumerate().into_list().unwrap()
            [(0, 'a'), (1, 'b')]
        """
        return Iter(enumerate(self._data))

    def partition(self, n: int, pad: T | None = None):
        """Partition into tuples of length n, optionally padded.

        Example:
            >>> Iter([1, 2, 3, 4]).partition(2).into_list().unwrap()
            [(1, 2), (3, 4)]
        """
        return Iter(cz.itertoolz.partition(n, self._data, pad))

    def partition_all(self, n: int):
        """Partition into tuples of length at most n.

        Example:
            >>> Iter([1, 2, 3]).partition_all(2).into_list().unwrap()
            [(1, 2), (3,)]
        """
        return Iter(cz.itertoolz.partition_all(n, self._data))

    def rolling(self, length: int):
        """Return sliding windows of the given length.

        Example:
            >>> Iter([1, 2, 3]).rolling(2).into_list().unwrap()
            [(1, 2), (2, 3)]
        """
        return Iter(cz.itertoolz.sliding_window(length, self._data))

    def cross_join(self, other: Iterable[T]):
        """Cartesian product with another iterable, wrapped as Iter.

        Example:
            >>> Iter([1, 2]).cross_join([10]).into_list().unwrap()
            [(1, 10), (2, 10)]
        """
        return Iter(itertools.product(self._data, other))

    def repeat(self, n: int):
        """Repeat the entire iterable n times (as elements) and return Iter.

        Example:
            >>> Iter([1, 2]).repeat(2).into_list().unwrap()
            [[1, 2], [1, 2]]
        """
        return Iter(itertools.repeat(self._data, n))

    def diff(
        self,
        *others: Iterable[T],
        key: Process[T] | None = None,
    ):
        """Yield differences between sequences.

        Example:
            >>> Iter([1, 2, 3]).diff([1, 2, 10]).into_list().unwrap()
            [(3, 10)]
        """
        return Iter(cz.itertoolz.diff(self._data, *others, ccpdefault=None, key=key))

    def zip_with(self, *others: Iterable[T], strict: bool = False):
        """Zip with other iterables, optionally strict, wrapped in Iter.

        Example:
            >>> Iter([1, 2]).zip_with([10, 20]).into_list().unwrap()
            [(1, 10), (2, 20)]
        """
        return Iter(zip(self._data, *others, strict=strict))

    def group_by[K, **P](self, on: Transform[T, K]):
        """Group elements by key function and return a Dict result.

        Example:
            >>> Iter(["a", "bb"]).group_by(len).unwrap()
            {1: ['a'], 2: ['bb']}
        """
        return Dict(cz.itertoolz.groupby(on, self._data))

    def into_frequencies(self):
        """Return a Dict of value frequencies.

        Example:
            >>> Iter([1, 1, 2]).into_frequencies().unwrap()
            {1: 2, 2: 1}
        """
        return Dict(cz.itertoolz.frequencies(self._data))

    def reduce_by[K](self, key: Transform[T, K], binop: Callable[[T, T], T]):
        """Reduce grouped elements by binop, returning a Iter of results.

        Example:
            >>> Iter([1, 2, 3, 4]).reduce_by(
            ...     lambda x: x % 2, lambda a, b: a + b
            ... ).into_list().unwrap()
            [1, 0]
        """
        return Iter(cz.itertoolz.reduceby(key, binop, self._data))

    def into_list(self):
        """Return the underlying list."""
        return List([*self._data])


@dataclass(slots=True)
class Dict[KT, VT](BaseDict[KT, VT], CommonBase[dict[KT, VT]]):
    """
    Public eager Dict wrapper providing chainable dict operations.

    Use this class for examples and interactive transformations. Methods
    return Dict instances wrapping the underlying mapping.
    """

    def pipe[KR, VR, **P](
        self,
        func: Callable[Concatenate[dict[KT, VT], P], dict[KR, VR]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Apply func to internal dict and wrap the result in Dict.

        Example:
            >>> Dict({1: 2}).pipe(lambda d: {**d, 3: 4}).unwrap()
            {1: 2, 3: 4}
        """
        return Dict(func(self._data, *args, **kwargs))

    def map_keys[T](self, f: Transform[KT, T]):
        """Return a Dict with keys transformed by f.

        Example:
            >>> Dict({1: "a"}).map_keys(str).unwrap()
            {'1': 'a'}
        """
        return Dict(cz.dicttoolz.keymap(f, self._data))

    def map_values[T](self, f: Transform[VT, T]):
        """Return a Dict with values transformed by f.

        Example:
            >>> Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
            {1: 2}
        """
        return Dict(cz.dicttoolz.valmap(f, self._data))

    def flatten_keys(self):
        """Flatten nested mappings into a single-level Dict with dotted keys.

        Example:
            >>> Dict({"a": {"b": 1}}).flatten_keys().unwrap()
            {'a.b': 1}
        """
        return Dict(flatten_recursive(self._data))

    def map_items[KR, VR](
        self,
        f: Transform[tuple[KT, VT], tuple[KR, VR]],
    ):
        """Transform (key, value) pairs using f and return a Dict.

        Example:
            >>> Dict({1: 2}).map_items(lambda kv: (kv[0] + 1, kv[1] * 10)).unwrap()
            {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(f, self._data))

    def map_keys_values[KR, VR](
        self,
        f: Callable[[KT, VT], tuple[KR, VR]],
    ):
        """Transform (key, value) pairs using f(key, value) and return a Dict.
        Internally unpack the key/value tuple, hence this method is syntactic sugar for map_items

        Example:
            >>> Dict({1: 2}).map_keys_values(lambda k, v: (k + 1, v * 10)).unwrap()
            {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(lambda kv: f(kv[0], kv[1]), self._data))

    def iter_keys(self):
        """Return a Iter of the dict's keys.

        Example:
            >>> Dict({1: 2}).iter_keys().into_list().unwrap()
            [1]
        """
        return Iter(self._data.keys())

    def iter_values(self):
        """Return a Iter of the dict's values.

        Example:
            >>> Dict({1: 2}).iter_values().into_list().unwrap()
            [2]
        """
        return Iter(self._data.values())

    def iter_items(self):
        """Return a Iter of the dict's items.

        Example:
            >>> Dict({1: 2}).iter_items().into_list().unwrap()
            [(1, 2)]
        """
        return Iter(self._data.items())


@dataclass(slots=True)
class List[T](BaseList[T], CommonBase[list[T]]):
    _data: list[T]

    def pipe[U, **P](
        self,
        func: Callable[Concatenate[list[T], P], list[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """
        Pass the list to a function and return a new List with the result.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).pipe(lambda x: [i * 2 for i in x]).unwrap()
            [2, 4]
        """
        return List(func(self._data, *args, **kwargs))

    def compose(self, *funcs: Process[list[T]]) -> Self:
        """
        Pass the list to a function and return a new List with the result.

        Example:
            >>> from ._lib import List
            >>> List([1, 2]).compose(lambda x: [i * 2 for i in x]).unwrap()
            [2, 4]
        """
        return self.__class__(cz.functoolz.pipe(self._data, *funcs))

    def into_iter(self) -> Iter[T]:
        """Return an iterator over the list's elements."""
        return Iter(iter(self._data))
