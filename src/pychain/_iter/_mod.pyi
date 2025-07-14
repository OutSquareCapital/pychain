from collections.abc import Callable, Iterable
from random import Random
from typing import Any, Self

import polars as pl
from numpy.typing import NDArray

from .._protocols import CheckFunc, ProcessFunc, TransformFunc

class Iter[V]:
    _value: Iterable[V]
    _pipeline: list[Callable[[Iterable[V]], Any]]

    def __init__(
        self,
        _value: Iterable[V],
        _pipeline: list[Callable[[Iterable[V]], Any]] | None = None,
    ) -> None: ...
    def clone(self) -> Self: ...
    def unwrap(self) -> Iterable[V]: ...
    def group_by[K](self, on: TransformFunc[V, K]) -> dict[K, list[V]]: ...
    def into_frequencies(self) -> dict[V, int]: ...
    def reduce_by[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "Iter[K]": ...
    def _do(self, f: ProcessFunc[Iterable[V]]) -> Self: ...
    def _into[V1](self, f: TransformFunc[Iterable[V], Iterable[V1]]) -> "Iter[V1]": ...
    def agg[V1](self, on: Callable[[Iterable[V]], V1]) -> V1: ...
    def map[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Structs a function over elements (like built-in map).

        Example:
            >>> Iter([1, 2]).map(lambda x: x * 2).to_list()
            [2, 4]
        """
        ...

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "Iter[V1]":
        """
        Structs a function and flattens the result (see cytoolz.concatmap).

        Example:
            >>> Iter([1, 2]).flat_map(lambda x: [x, x + 10]).to_list()
            [1, 11, 2, 12]
        """
        ...

    def starmap[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Structs a function over elements, unpacking each tuple element as arguments
        (like itertools.starmap).

        Example:
            >>> data = [(1, 2), (3, 4)]
            >>> def add(x, y): ...
            >>> Iter(data).starmap(add).to_list()
            [3, 7]
        """
        ...

    def compose[V1](self, *fns: TransformFunc[V, V1]) -> "Iter[V1]": ...
    def take_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Takes elements while predicate is true (like itertools.takewhile).

        Example:
            >>> Iter([1, 2, 3, 2]).take_while(lambda x: x < 3).to_list()
            [1, 2]
        """
        ...

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Drops elements while predicate is true (like itertools.dropwhile).

        Example:
            >>> Iter([1, 2, 3, 2]).drop_while(lambda x: x < 3).to_list()
            [3, 2]
        """
        ...

    def interleave(self, *others: Iterable[V]) -> Self:
        """
        Interleaves the iterable with other iterables (see cytoolz.interleave).

        Example:
            >>> Iter([1, 2]).interleave([10, 20]).to_list()
            [1, 10, 2, 20]
        """
        ...

    def interpose(self, element: V) -> Self:
        """
        Inserts the given element between each pair of elements (see cytoolz.interpose).

        Example:
            >>> Iter([1, 2, 3]).interpose(0).to_list()
            [1, 0, 2, 0, 3]
        """
        ...

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        """
        ...

        Example:
            >>> Iter([1, 5, 3, 2]).top_n(2).to_list()
            [5, 3]
        """
        ...

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly samples elements with given probability (see cytoolz.random_sample).

        Example:
            >>> Iter(range(100)).random_sample(probability=0.01, state=1).to_list()
            [13, 91]
        """
        ...

    def concat(self, *others: Iterable[V]) -> Self:
        """
        Concatenates the iterable with others (see cytoolz.concat).

        Example:
            >>> Iter([1, 2]).concat([3, 4]).to_list()
            [1, 2, 3, 4]
        """
        ...

    def filter(self, f: CheckFunc[V]) -> Self:
        """
        Filters elements by predicate (like built-in filter).

        Example:
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).to_list()
            [2, 3]
        """
        ...

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Accumulates values using binary function (see cytoolz.accumulate).

        Example:
            >>> Iter([1, 2, 3]).accumulate(lambda x, y: x + y).to_list()
            [1, 3, 6]
        """
        ...

    def insert_left(self, value: V) -> Self:
        """
        Prepends a value (see cytoolz.cons).

        Example:
            >>> Iter([2, 3]).insert_left(1).to_list()
            [1, 2, 3]
        """
        ...

    def peek(self, note: str | None = None) -> Self:
        """
        Peeks at elements, printing them optionally with a note.

        Example:
            >>> Iter([1, 2, 3]).peek("step 1").to_list()
            Peeked value (step 1): 1
            [1, 2, 3]
        """
        ...

    def peekn(self, n: int, note: str | None = None) -> Self:
        """
        Peeks at first n elements, printing them optionally with a note.

        Example:
            >>> Iter([1, 2, 3, 4, 5, 6]).peekn(3, "step 1").to_list()
            Peeked 3 values (step 1): [1, 2, 3]
            [1, 2, 3, 4, 5, 6]
        """
        ...

    def head(self, n: int) -> Self:
        """
        Takes first n elements (see cytoolz.take).

        Example:
            >>> Iter([1, 2, 3, 4]).head(2).to_list()
            [1, 2]
        """
        ...

    def tail(self, n: int) -> Self:
        """
        Takes last n elements (see cytoolz.tail).

        Example:
            >>> Iter([1, 2, 3, 4]).tail(2).to_list()
            [3, 4]
        """
        ...

    def drop_first(self, n: int) -> Self:
        """
        Drops first n elements (see cytoolz.drop).

        Example:
            >>> Iter([1, 2, 3, 4]).drop_first(2).to_list()
            [3, 4]
        """
        ...

    def every(self, index: int) -> Self:
        """
        Takes every index-th element (see cytoolz.take_nth).

        Example:
            >>> Iter([0, 1, 2, 3, 4]).every(2).to_list()
            [0, 2, 4]
        """
        ...

    def repeat(self, n: int) -> Self:
        """
        Repeats the iterable n times (see cytoolz.repeat).

        Example:
            >>> Iter([1, 2]).repeat(2).to_list()
            [1, 1, 2, 2]
        """
        ...

    def unique(self) -> Self:
        """
        ...

        Example:
            >>> Iter([1, 2, 2, 3]).unique().to_list()
            [1, 2, 3]
        """
        ...

    def cumsum(self) -> Self:
        """
        Computes cumulative sum (see cytoolz.accumulate with operator.add).

        Example:
            >>> Iter([1, 2, 3]).cumsum().to_list()
            [1, 3, 6]
        """
        ...

    def cumprod(self) -> Self:
        """
        Computes cumulative product (see cytoolz.accumulate with operator.mul).

        Example:
            >>> Iter([1, 2, 3]).cumprod().to_list()
            [1, 2, 6]
        """
        ...

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        """
        Merges and sorts with other iterables (see cytoolz.merge_sorted).

        Example:
            >>> Iter([1, 3]).merge_sorted([2, 4]).to_list()
            [1, 2, 3, 4]
        """
        ...

    def tap(self, func: Callable[[V], None]) -> Self:
        """
        Applies a side-effect function to each element (see cytoolz.do/tap).

        Example:
            >>> Iter([1, 2]).tap(print).to_list()
            1
            2
            [1, 2]
        """
        ...

    def zip_with(
        self, *others: Iterable[V], strict: bool = False
    ) -> "Iter[tuple[V, ...]]":
        """
        Zips with other iterables (like built-in zip).

        Example:
            >>> Iter([1, 2]).zip_with([10, 20]).to_list()
            [(1, 10), (2, 20)]
        """
        ...

    def enumerate(self) -> "Iter[tuple[int, V]]":
        """
        Enumerates the iterable (like built-in enumerate).

        Example:
            >>> Iter(["a", "b"]).enumerate().to_list()
            [(0, 'a'), (1, 'b')]
        """
        ...

    def flatten(self) -> "Iter[Any]":
        """
        Flattens nested iterables (see cytoolz.concat).

        Example:
            >>> Iter([[1, 2], [3, 4]]).flatten().to_list()
            [1, 2, 3, 4]
        """
        ...

    def diff(
        self,
        *others: Iterable[V],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ) -> "Iter[tuple[V, ...]]":
        """
        Compute the difference between iterables (see cytoolz.diff).

        ...

        Example:
            >>> Iter([1, 2, 3]).diff([1, 2, 10, 100]).to_list()
            [(3, 10), (None, 100)]

            You can replace `None` with a custom default[V] value:

            >>> Iter([1, 2, 3]).diff([1, 2, 10, 100], default[V]="foo").to_list()
            [(3, 10), ('foo', 100)]

            A key function may also be applied to each item to use during comparisons:

            >>> Iter(["apples", "bananas"]).diff(
            ...     ["Apples", "Oranges"], key=str.lower
            ... ).to_list()
            [('bananas', 'Oranges')]
        """
        ...

    def partition(self, n: int, pad: V | None = None) -> "Iter[tuple[V, ...]]":
        """
        Partitions into chunks of size n, padding last if needed (see cytoolz.partition).

        Example:
            >>> Iter([1, 2, 3, 4, 5]).partition(2, pad=0).to_list()
            [(1, 2), (3, 4), (5, 0)]
        """
        ...

    def partition_all(self, n: int) -> "Iter[tuple[V, ...]]":
        """
        Partitions into chunks of size n, last chunk may be smaller (see cytoolz.partition_all).

        Example:
            >>> Iter([1, 2, 3, 4, 5]).partition_all(2).to_list()
            [(1, 2), (3, 4), (5,)]
        """
        ...

    def rolling(self, length: int) -> "Iter[tuple[V, ...]]":
        """
        Creates a sliding window of given length (see cytoolz.sliding_window).

        Example:
            >>> Iter([1, 2, 3, 4]).rolling(3).to_list()
            [(1, 2, 3), (2, 3, 4)]
        """
        ...

    def cross_join[V1](self, other: Iterable[V1]) -> "Iter[tuple[V1, V]]":
        """
        Creates an Iter from the Cartesian product of input iterables.

        Example:
            >>> Iter(range(0, 2)).cross_join(["a", "b"]).to_list()
            [('a', 0), ('a', 1), ('b', 0), ('b', 1)]
        """
        ...

    def first(self) -> V: ...
    def second(self) -> V: ...
    def last(self) -> V: ...
    def at_index(self, index: int) -> V: ...
    def len(self) -> int: ...
    def to_obj[T](self, obj: Callable[[Iterable[V]], T]) -> T: ...
    def to_list(self) -> list[V]: ...
    def to_set(self) -> set[V]: ...
    def to_dict(self) -> dict[int, V]: ...
    def to_array(self) -> NDArray[Any]: ...
    def to_series(self) -> pl.Series: ...
    def to_frame(self) -> pl.DataFrame: ...
