from collections.abc import Callable, Iterable
from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING, Any, Self

import numpy as np
import polars as pl
from numpy.typing import NDArray

from ..._fn import agg, fn, it
from ..._protocols import CheckFunc, ProcessFunc, TransformFunc
from ._core import AbstractChain

if TYPE_CHECKING:
    from .._main import Iter



@dataclass(slots=True, frozen=True, repr=False)
class BaseIter[V](AbstractChain[Iterable[V]]):

    def agg[V1](self, on: Callable[[Iterable[V]], V1]) -> V1:
        return on(self.unwrap())

    def into[V1](self, f: TransformFunc[Iterable[V], Iterable[V1]]) -> "Iter[V1]":
        """
        Transforms the iterable using the provided function, returning a new chain.

        Example:
            >>> BaseIter([1, 2, 3]).into(reversed).to_list()
            [3, 2, 1]
        """
        return self.__class__(
            _value=self._value,
            _pipeline=[fn.compose(*self._pipeline, f)],
        )  # type: ignore

    def map[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Structs a function over elements (like built-in map).

        Example:
            >>> BaseIter([1, 2]).map(lambda x: x * 2).to_list()
            [2, 4]
        """
        return self.into(f=fn.partial_map(f))

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "Iter[V1]":
        """
        Structs a function and flattens the result (see cytoolz.concatmap).

        Example:
            >>> BaseIter([1, 2]).flat_map(lambda x: [x, x + 10]).to_list()
            [1, 11, 2, 12]
        """
        return self.into(f=fn.flat_map(f))

    def starmap[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Structs a function over elements, unpacking each tuple element as arguments
        (like itertools.starmap).

        Example:
            >>> data = [(1, 2), (3, 4)]
            >>> def add(x, y):
            ...     return x + y
            >>> BaseIter(data).starmap(add).to_list()
            [3, 7]
        """
        return self.into(f=it.starmap(f))

    def compose[V1](self, *fns: TransformFunc[V, V1]) -> "Iter[V1]":
        return self.into(f=fn.compose_on_iter(*fns))

    def take_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Takes elements while predicate is true (like itertools.takewhile).

        Example:
            >>> BaseIter([1, 2, 3, 2]).take_while(lambda x: x < 3).to_list()
            [1, 2]
        """
        return self.do(f=it.take_while(predicate))

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Drops elements while predicate is true (like itertools.dropwhile).

        Example:
            >>> BaseIter([1, 2, 3, 2]).drop_while(lambda x: x < 3).to_list()
            [3, 2]
        """
        return self.do(f=it.drop_while(predicate))

    def interleave(self, *others: Iterable[V]) -> Self:
        """
        Interleaves the iterable with other iterables (see cytoolz.interleave).

        Example:
            >>> BaseIter([1, 2]).interleave([10, 20]).to_list()
            [1, 10, 2, 20]
        """
        return self.do(f=it.interleave(others))

    def interpose(self, element: V) -> Self:
        """
        Inserts the given element between each pair of elements (see cytoolz.interpose).

        Example:
            >>> BaseIter([1, 2, 3]).interpose(0).to_list()
            [1, 0, 2, 0, 3]
        """
        return self.do(f=it.interpose(element))

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        """
        Returns the top n elements based on the key (see cytoolz.topk).

        Example:
            >>> BaseIter([1, 5, 3, 2]).top_n(2).to_list()
            [5, 3]
        """
        return self.do(f=it.top_n(n=n, key=key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly samples elements with given probability (see cytoolz.random_sample).

        Example:
            >>> BaseIter(range(100)).random_sample(
            ...     probability=0.01, state=1
            ... ).to_list()
            [13, 91]
        """
        return self.do(f=it.random_sample(probability=probability, state=state))

    def concat(self, *others: Iterable[V]) -> Self:
        """
        Concatenates the iterable with others (see cytoolz.concat).

        Example:
            >>> BaseIter([1, 2]).concat([3, 4]).to_list()
            [1, 2, 3, 4]
        """
        return self.do(f=it.concat(others))

    def filter(self, f: CheckFunc[V]) -> Self:
        """
        Filters elements by predicate (like built-in filter).

        Example:
            >>> BaseIter([1, 2, 3]).filter(lambda x: x > 1).to_list()
            [2, 3]
        """
        return self.do(f=fn.partial_filter(f))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Accumulates values using binary function (see cytoolz.accumulate).

        Example:
            >>> BaseIter([1, 2, 3]).accumulate(lambda x, y: x + y).to_list()
            [1, 3, 6]
        """
        return self.do(f=it.accumulate(f=f))

    def insert_left(self, value: V) -> Self:
        """
        Prepends a value (see cytoolz.cons).

        Example:
            >>> BaseIter([2, 3]).insert_left(1).to_list()
            [1, 2, 3]
        """
        return self.do(f=it.insert_left(value))

    def peek(self, note: str | None = None) -> Self:
        """
        Peeks at elements, printing them optionally with a note.

        Example:
            >>> BaseIter([1, 2, 3]).peek("step 1").to_list()
            Peeked value (step 1): 1
            [1, 2, 3]
        """
        return self.do(f=it.peek(note=note))

    def peekn(self, n: int, note: str | None = None) -> Self:
        """
        Peeks at first n elements, printing them optionally with a note.

        Example:
            >>> BaseIter([1, 2, 3, 4, 5, 6]).peekn(3, "step 1").to_list()
            Peeked 3 values (step 1): [1, 2, 3]
            [1, 2, 3, 4, 5, 6]
        """
        return self.do(f=it.peekn(n=n, note=note))

    def head(self, n: int) -> Self:
        """
        Takes first n elements (see cytoolz.take).

        Example:
            >>> BaseIter([1, 2, 3, 4]).head(2).to_list()
            [1, 2]
        """
        return self.do(f=it.head(n=n))

    def tail(self, n: int) -> Self:
        """
        Takes last n elements (see cytoolz.tail).

        Example:
            >>> BaseIter([1, 2, 3, 4]).tail(2).to_list()
            [3, 4]
        """
        return self.do(f=it.tail(n=n))

    def drop_first(self, n: int) -> Self:
        """
        Drops first n elements (see cytoolz.drop).

        Example:
            >>> BaseIter([1, 2, 3, 4]).drop_first(2).to_list()
            [3, 4]
        """
        return self.do(f=it.drop_first(n=n))

    def every(self, index: int) -> Self:
        """
        Takes every index-th element (see cytoolz.take_nth).

        Example:
            >>> BaseIter([0, 1, 2, 3, 4]).every(2).to_list()
            [0, 2, 4]
        """
        return self.do(f=it.every(index=index))

    def repeat(self, n: int) -> Self:
        """
        Repeats the iterable n times (see cytoolz.repeat).

        Example:
            >>> BaseIter([1, 2]).repeat(2).to_list()
            [1, 1, 2, 2]
        """
        return self.do(f=it.repeat(n=n))

    def unique(self) -> Self:
        """
        Returns unique elements (see cytoolz.unique).

        Example:
            >>> BaseIter([1, 2, 2, 3]).unique().to_list()
            [1, 2, 3]
        """
        return self.do(f=it.unique)

    def cumsum(self) -> Self:
        """
        Computes cumulative sum (see cytoolz.accumulate with operator.add).

        Example:
            >>> BaseIter([1, 2, 3]).cumsum().to_list()
            [1, 3, 6]
        """
        return self.do(f=it.cumsum())

    def cumprod(self) -> Self:
        """
        Computes cumulative product (see cytoolz.accumulate with operator.mul).

        Example:
            >>> BaseIter([1, 2, 3]).cumprod().to_list()
            [1, 2, 6]
        """
        return self.do(f=it.cumprod())

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        """
        Merges and sorts with other iterables (see cytoolz.merge_sorted).

        Example:
            >>> BaseIter([1, 3]).merge_sorted([2, 4]).to_list()
            [1, 2, 3, 4]
        """
        return self.do(f=it.merge_sorted(others=others, sort_on=sort_on))

    def tap(self, func: Callable[[V], None]) -> Self:
        """
        Applies a side-effect function to each element (see cytoolz.do/tap).

        Example:
            >>> BaseIter([1, 2]).tap(print).to_list()
            1
            2
            [1, 2]
        """
        return self.do(f=it.tap(func=func))

    def zip_with(
        self, *others: Iterable[Any], strict: bool = False
    ) -> "Iter[tuple[V, ...]]":
        """
        Zips with other iterables (like built-in zip).

        Example:
            >>> BaseIter([1, 2]).zip_with([10, 20]).to_list()
            [(1, 10), (2, 20)]
        """
        return self.into(f=it.zip_with(others=others, strict=strict))

    def enumerate(self) -> "Iter[tuple[int, V]]":
        """
        Enumerates the iterable (like built-in enumerate).

        Example:
            >>> BaseIter(["a", "b"]).enumerate().to_list()
            [(0, 'a'), (1, 'b')]
        """
        return self.into(f=enumerate)

    def flatten(self) -> "Iter[Any]":
        """
        Flattens nested iterables (see cytoolz.concat).

        Example:
            >>> BaseIter([[1, 2], [3, 4]]).flatten().to_list()
            [1, 2, 3, 4]
        """
        return self.into(f=it.flatten)

    def diff(
        self,
        *others: Iterable[V],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ) -> "Iter[tuple[V, ...]]":
        """
        Compute the difference between iterables (see cytoolz.diff).

        Return those items that differ between sequences.

        Example:
            >>> BaseIter([1, 2, 3]).diff([1, 2, 10, 100]).to_list()
            [(3, 10), (None, 100)]

            You can replace `None` with a custom default value:

            >>> BaseIter([1, 2, 3]).diff([1, 2, 10, 100], default="foo").to_list()
            [(3, 10), ('foo', 100)]

            A key function may also be applied to each item to use during comparisons:

            >>> BaseIter(["apples", "bananas"]).diff(
            ...     ["Apples", "Oranges"], key=str.lower
            ... ).to_list()
            [('bananas', 'Oranges')]
        """
        return self.into(f=it.diff(others=others, default=default, key=key))

    def partition(self, n: int, pad: V | None = None) -> "Iter[tuple[V, ...]]":
        """
        Partitions into chunks of size n, padding last if needed (see cytoolz.partition).

        Example:
            >>> BaseIter([1, 2, 3, 4, 5]).partition(2, pad=0).to_list()
            [(1, 2), (3, 4), (5, 0)]
        """
        return self.into(f=it.partition(n=n, pad=pad))

    def partition_all(self, n: int) -> "Iter[tuple[V, ...]]":
        """
        Partitions into chunks of size n, last chunk may be smaller (see cytoolz.partition_all).

        Example:
            >>> BaseIter([1, 2, 3, 4, 5]).partition_all(2).to_list()
            [(1, 2), (3, 4), (5,)]
        """
        return self.into(f=it.partition_all(n))

    def rolling(self, length: int) -> "Iter[tuple[V, ...]]":
        """
        Creates a sliding window of given length (see cytoolz.sliding_window).

        Example:
            >>> BaseIter([1, 2, 3, 4]).rolling(3).to_list()
            [(1, 2, 3), (2, 3, 4)]
        """
        return self.into(f=it.rolling(length=length))

    def cross_join[V1](self, other: Iterable[V1]) -> "Iter[tuple[V1, V]]":
        """
        Creates an Iter from the Cartesian product of input iterables.

        Example:
            >>> BaseIter(range(0, 2)).cross_join(["a", "b"]).to_list()
            [('a', 0), ('a', 1), ('b', 0), ('b', 1)]
        """
        return self.into(it.cross_join(other=other))

    def first(self) -> V:
        return agg.first(self.unwrap())

    def second(self) -> V:
        return agg.second(self.unwrap())

    def last(self) -> V:
        return agg.last(self.unwrap())

    def at_index(self, index: int) -> V:
        return agg.at_index(index=index)(self.unwrap())

    def len(self) -> int:
        return agg.length(self.unwrap())

    def to_obj[T](self, obj: Callable[[Iterable[V]], T]) -> T:
        return obj(self.unwrap())

    def to_list(self) -> list[V]:
        return list(self.unwrap())

    def to_set(self) -> set[V]:
        return set(self.unwrap())

    def to_dict(self) -> dict[int, V]:
        return dict(enumerate(self.unwrap()))

    def to_array(self) -> NDArray[Any]:
        return np.array(self.unwrap())

    def to_series(self) -> pl.Series:
        return pl.Series(self.unwrap())

    def to_frame(self) -> pl.DataFrame:
        return pl.DataFrame(self.to_dict())
