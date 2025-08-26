import itertools
from collections.abc import Callable
from typing import Concatenate

import cytoolz.dicttoolz as dcz
import cytoolz.itertoolz as itz

from ._core import CommonBase, Process, Transform, flatten_recursive
from ._dict import BaseDict
from ._list import BaseList


class List[T](BaseList[T], CommonBase[list[T]]):
    """
    Public eager List wrapper providing chainable list operations.

    Use this class for examples and interactive transformations. Methods
    return List instances wrapping the underlying Python list.
    """

    def pipe[U, **P](
        self,
        func: Callable[Concatenate[list[T], P], list[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Apply func to the internal list and wrap the result in List.

        Example:
            >>> List([1, 2]).pipe(lambda lst: [x * 2 for x in lst]).data
            [2, 4]
        """
        return List(func(self.data, *args, **kwargs))

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ):
        """Map each element through func and return a List of results.

        Example:
            >>> List([1, 2]).map(lambda x: x + 1).data
            [2, 3]
        """
        return List(map(func, self.data, *args, **kwargs))

    def flat_map[R, **P](
        self,
        func: Callable[Concatenate[T, P], list[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Apply func producing iterables and flatten the results into a List.

        Example:
            >>> List([1, 2]).flat_map(lambda x: [x, -x]).data
            [1, -1, 2, -2]
        """
        return List(itz.concat(map(func, self.data, *args, **kwargs)))

    def enumerate(self):
        """Return a List of (index, value) pairs.

        Example:
            >>> List(["a", "b"]).enumerate().data
            [(0, 'a'), (1, 'b')]
        """
        return List(enumerate(self.data))

    def partition(self, n: int, pad: T | None = None):
        """Partition into tuples of length n, optionally padded.

        Example:
            >>> List([1, 2, 3, 4]).partition(2).data
            [(1, 2), (3, 4)]
        """
        return List(itz.partition(n, self.data, pad))

    def partition_all(self, n: int):
        """Partition into tuples of length at most n.

        Example:
            >>> List([1, 2, 3]).partition_all(2).data
            [(1, 2), (3,)]
        """
        return List(itz.partition_all(n, self.data))

    def rolling(self, length: int):
        """Return sliding windows of the given length.

        Example:
            >>> List([1, 2, 3]).rolling(2).data
            [(1, 2), (2, 3)]
        """
        return List(itz.sliding_window(length, self.data))

    def cross_join(self, other: list[T]):
        """Cartesian product with another list, wrapped as List.

        Example:
            >>> List([1, 2]).cross_join([10]).data
            [(1, 10), (2, 10)]
        """
        return List(itertools.product(self.data, other))

    def repeat(self, n: int):
        """Repeat the entire list n times (as elements) and return List.

        Example:
            >>> List([1, 2]).repeat(2).data
            [[1, 2], [1, 2]]
        """
        return List(itertools.repeat(self.data, n))

    def diff(
        self,
        *others: list[T],
        key: Process[T] | None = None,
    ):
        """Yield differences between sequences.

        Example:
            >>> List([1, 2, 3]).diff([1, 2, 10]).data
            [(3, 10)]
        """
        return List(itz.diff(self.data, *others, ccpdefault=None, key=key))

    def zip_with(self, *others: list[T], strict: bool = False):
        """Zip with other lists, optionally strict, wrapped in List.

        Example:
            >>> List([1, 2]).zip_with([10, 20]).data
            [(1, 10), (2, 20)]
        """
        return List(zip(self.data, *others, strict=strict))

    def group_by[K, **P](self, on: Transform[T, K]):
        """Group elements by key function and return a Dict result.

        Example:
            >>> List(["a", "bb"]).group_by(len).data
            {1: ['a'], 2: ['bb']}
        """
        return Dict(itz.groupby(on, self.data))

    def into_frequencies(self):
        """Return a Dict of value frequencies.

        Example:
            >>> List([1, 1, 2]).into_frequencies().data
            {1: 2, 2: 1}
        """
        return Dict(itz.frequencies(self.data))

    def reduce_by[K](self, key: Transform[T, K], binop: Callable[[T, T], T]):
        """Reduce grouped elements by binop, returning a List of results.

        Example:
            >>> List([1, 2, 3, 4]).reduce_by(lambda x: x % 2, lambda a, b: a + b)
            [1, 0]
        """
        return List(itz.reduceby(key, binop, self.data))


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
            >>> Dict({1: 2}).pipe(lambda d: {**d, 3: 4}).data
            {1: 2, 3: 4}
        """
        return Dict(func(self.data, *args, **kwargs))

    def map_keys[T](self, f: Transform[KT, T]):
        """Return a Dict with keys transformed by f.

        Example:
            >>> Dict({1: "a"}).map_keys(str).data
            {'1': 'a'}
        """
        return Dict(dcz.keymap(f, self.data))

    def map_values[T](self, f: Transform[VT, T]):
        """Return a Dict with values transformed by f.

        Example:
            >>> Dict({1: 1}).map_values(lambda v: v + 1).data
            {1: 2}
        """
        return Dict(dcz.valmap(f, self.data))

    def flatten_keys(self):
        """Flatten nested mappings into a single-level Dict with dotted keys.

        Example:
            >>> Dict({"a": {"b": 1}}).flatten_keys().data
            {'a.b': 1}
        """
        return Dict(flatten_recursive(self.data))

    def map_items[KR, VR](
        self,
        f: Transform[tuple[KT, VT], tuple[KR, VR]],
    ):
        """Transform (key, value) pairs using f and return a Dict.

        Example:
            >>> Dict({1: 2}).map_items(lambda kv: (kv[0] + 1, kv[1] * 10)).data
            {2: 20}
        """
        return Dict(dcz.itemmap(f, self.data))

    def map_keys_values[KR, VR](
        self,
        f: Callable[[KT, VT], tuple[KR, VR]],
    ):
        """Transform (key, value) pairs using f(key, value) and return a Dict.
        Internally unpack the key/value tuple, hence this method is syntactic sugar for map_items

        Example:
            >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).data
            {2: 20}
        """
        return Dict(dcz.itemmap(lambda kv: f(kv[0], kv[1]), self.data))

    def list_keys(self):
        """Return a List of the dict's keys.

        Example:
            >>> Dict({1: 2}).list_keys().data
            [1]
        """
        return List(self.data.keys())

    def list_values(self):
        """Return a List of the dict's values.

        Example:
            >>> Dict({1: 2}).list_values().data
            [2]
        """
        return List(self.data.values())

    def list_items(self):
        """Return a List of the dict's items.

        Example:
            >>> Dict({1: 2}).list_items().data
            [(1, 2)]
        """
        return List(self.data.items())
