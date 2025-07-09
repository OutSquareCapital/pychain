import functools as ft
import itertools as it
import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz

from ._lazyfuncs import (
    TransformFunc,
    CheckFunc,
    Random,
    ProcessFunc,
    interleave,
    concat,
    repeat,
    merge_sorted,
    zip_with,
    diff_with,
    flat_map,
    peek,
    peekn,
    tap,
)
from ._core import AbstractChain
from ._executors import Checker, Converter

if TYPE_CHECKING:
    from ._implementations import IterChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseIterChain[V](AbstractChain[Iterable[V]]):
    _value: Iterable[V]

    @property
    def convert_to(self) -> Converter[V]:
        """
        Returns a Converter for the iterable, providing methods to convert to list, set, array, etc.

        Example:
            >>> BaseIterChain([1, 2, 3]).convert_to.list()
            [1, 2, 3]
        """
        return Converter(_value=self.unwrap())

    @property
    def check_if(self) -> Checker[V]:
        """
        Returns a Checker for the iterable, providing boolean checks like all, any, distinct, etc.

        Example:
            >>> BaseIterChain([1, 2, 3]).check_if.all()
            True
        """
        return Checker(_value=self.unwrap())

    def into[V1](self, f: TransformFunc[Iterable[V], Iterable[V1]]) -> "IterChain[V1]":
        """
        Transforms the iterable using the provided function, returning a new chain.

        Example:
            >>> BaseIterChain([1, 2, 3]).into(reversed).convert_to.list()
            [3, 2, 1]
        """
        return self.__class__(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def take_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Takes elements while predicate is true (like itertools.takewhile).

        Example:
            >>> BaseIterChain([1, 2, 3, 2]).take_while(
            ...     lambda x: x < 3
            ... ).convert_to.list()
            [1, 2]
        """
        return self.do(f=ft.partial(it.takewhile, predicate))

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Drops elements while predicate is true (like itertools.dropwhile).

        Example:
            >>> BaseIterChain([1, 2, 3, 2]).drop_while(
            ...     lambda x: x < 3
            ... ).convert_to.list()
            [3, 2]
        """
        return self.do(f=ft.partial(it.dropwhile, predicate))

    def interleave(self, *others: Iterable[V]) -> Self:
        """
        Interleaves the iterable with other iterables (see cytoolz.interleave).

        Example:
            >>> BaseIterChain([1, 2]).interleave([10, 20]).convert_to.list()
            [1, 10, 2, 20]
        """
        return self.do(f=ft.partial(interleave, others=others))

    def interpose(self, element: V) -> Self:
        """
        Inserts the given element between each pair of elements (see cytoolz.interpose).

        Example:
            >>> BaseIterChain([1, 2, 3]).interpose(0).convert_to.list()
            [1, 0, 2, 0, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.interpose, element))

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        """
        Returns the top n elements based on the key (see cytoolz.topk).

        Example:
            >>> BaseIterChain([1, 5, 3, 2]).top_n(2).convert_to.list()
            [5, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.topk, n, key=key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly samples elements with given probability (see cytoolz.random_sample).

        Example:
            >>> len(
            ...     BaseIterChain(range(100)).random_sample(0.1).convert_to.list()
            ... )  # ~10
        """
        return self.do(
            f=ft.partial(
                cz.itertoolz.random_sample, prob=probability, random_state=state
            )
        )

    def concat(self, *others: Iterable[V]) -> Self:
        """
        Concatenates the iterable with others (see cytoolz.concat).

        Example:
            >>> BaseIterChain([1, 2]).concat([3, 4]).convert_to.list()
            [1, 2, 3, 4]
        """
        return self.do(f=ft.partial(concat, others=others))

    def filter(self, f: CheckFunc[V]) -> Self:
        """
        Filters elements by predicate (like built-in filter).

        Example:
            >>> BaseIterChain([1, 2, 3]).filter(lambda x: x > 1).convert_to.list()
            [2, 3]
        """
        return self.do(f=ft.partial(filter, f))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Accumulates values using binary function (see cytoolz.accumulate).

        Example:
            >>> BaseIterChain([1, 2, 3]).accumulate(
            ...     lambda x, y: x + y
            ... ).convert_to.list()
            [1, 3, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, f))

    def insert_left(self, value: V) -> Self:
        """
        Prepends a value (see cytoolz.cons).

        Example:
            >>> BaseIterChain([2, 3]).insert_left(1).convert_to.list()
            [1, 2, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.cons, value))

    def peek(self, note: str | None = None) -> Self:
        """
        Peeks at elements, printing them optionally with a note.

        Example:
            >>> BaseIterChain([1, 2, 3]).peek("step 1").convert_to.list()
            Peeked value (step 1): 1
            [1, 2, 3]
        """
        return self.do(f=ft.partial(peek, note=note))

    def peekn(self, n: int, note: str | None = None) -> Self:
        """
        Peeks at first n elements, printing them optionally with a note.

        Example:
            >>> BaseIterChain([1, 2, 3, 4, 5, 6]).peekn(3, "step 1").convert_to.list()
            Peeked 3 values (step 1): [1, 2, 3]
            [1, 2, 3, 4, 5, 6]
        """
        return self.do(f=ft.partial(peekn, n=n, note=note))

    def head(self, n: int) -> Self:
        """
        Takes first n elements (see cytoolz.take).

        Example:
            >>> BaseIterChain([1, 2, 3, 4]).head(2).convert_to.list()
            [1, 2]
        """
        return self.do(f=ft.partial(cz.itertoolz.take, n))

    def tail(self, n: int) -> Self:
        """
        Takes last n elements (see cytoolz.tail).

        Example:
            >>> BaseIterChain([1, 2, 3, 4]).tail(2).convert_to.list()
            [3, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.tail, n))

    def drop_first(self, n: int) -> Self:
        """
        Drops first n elements (see cytoolz.drop).

        Example:
            >>> BaseIterChain([1, 2, 3, 4]).drop_first(2).convert_to.list()
            [3, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.drop, n))

    def every(self, index: int) -> Self:
        """
        Takes every index-th element (see cytoolz.take_nth).

        Example:
            >>> BaseIterChain([0, 1, 2, 3, 4]).every(2).convert_to.list()
            [0, 2, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.take_nth, index))

    def repeat(self, n: int) -> Self:
        """
        Repeats the iterable n times (see cytoolz.repeat).

        Example:
            >>> BaseIterChain([1, 2]).repeat(2).convert_to.list()
            [1, 1, 2, 2]
        """
        return self.do(f=ft.partial(repeat, n=n))

    def unique(self) -> Self:
        """
        Returns unique elements (see cytoolz.unique).

        Example:
            >>> BaseIterChain([1, 2, 2, 3]).unique().convert_to.list()
            [1, 2, 3]
        """
        return self.do(f=cz.itertoolz.unique)

    def cumsum(self) -> Self:
        """
        Computes cumulative sum (see cytoolz.accumulate with operator.add).

        Example:
            >>> BaseIterChain([1, 2, 3]).cumsum().convert_to.list()
            [1, 3, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.add))

    def cumprod(self) -> Self:
        """
        Computes cumulative product (see cytoolz.accumulate with operator.mul).

        Example:
            >>> BaseIterChain([1, 2, 3]).cumprod().convert_to.list()
            [1, 2, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.mul))

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        """
        Merges and sorts with other iterables (see cytoolz.merge_sorted).

        Example:
            >>> BaseIterChain([1, 3]).merge_sorted([2, 4]).convert_to.list()
            [1, 2, 3, 4]
        """
        return self.do(f=ft.partial(merge_sorted, others=others, sort_on=sort_on))

    def tap(self, func: Callable[[V], None]) -> Self:
        """
        Applies a side-effect function to each element (see cytoolz.do/tap).

        Example:
            >>> BaseIterChain([1, 2]).tap(print).convert_to.list()
            1
            2
            [1, 2]
        """
        return self.do(f=ft.partial(tap, func=func))

    def zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> "IterChain[tuple[V, ...]]":
        """
        Zips with other iterables (like built-in zip).

        Example:
            >>> BaseIterChain([1, 2]).zip([10, 20]).convert_to.list()
            [(1, 10), (2, 20)]
        """
        return self.into(f=ft.partial(zip_with, others=others, strict=strict))

    def enumerate(self) -> "IterChain[tuple[int, V]]":
        """
        Enumerates the iterable (like built-in enumerate).

        Example:
            >>> BaseIterChain(["a", "b"]).enumerate().convert_to.list()
            [(0, 'a'), (1, 'b')]
        """
        return self.into(f=enumerate)

    def map[V1](self, f: TransformFunc[V, V1]) -> "IterChain[V1]":
        """
        Maps a function over elements (like built-in map).

        Example:
            >>> BaseIterChain([1, 2]).map(lambda x: x * 2).convert_to.list()
            [2, 4]
        """
        return self.into(f=ft.partial(map, f))

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "IterChain[V1]":
        """
        Maps a function and flattens the result (see cytoolz.concatmap).

        Example:
            >>> BaseIterChain([1, 2]).flat_map(lambda x: [x, x + 10]).convert_to.list()
            [1, 11, 2, 12]
        """
        return self.into(f=ft.partial(flat_map, func=f))

    def flatten(self) -> "IterChain[Any]":
        """
        Flattens nested iterables (see cytoolz.concat).

        Example:
            >>> BaseIterChain([[1, 2], [3, 4]]).flatten().convert_to.list()
            [1, 2, 3, 4]
        """
        return self.into(f=cz.itertoolz.concat)

    def diff(
        self,
        *others: Iterable[V],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ) -> "IterChain[tuple[V, ...]]":
        """
        Compute the difference between iterables (see cytoolz.diff).

        Return those items that differ between sequences.

        Example:
            >>> BaseIterChain([1, 2, 3]).diff([1, 2, 10, 100]).convert_to.list()
            [(3, 10), (None, 100)]

            You can replace `None` with a custom default value:

            >>> BaseIterChain([1, 2, 3]).diff(
            ...     [1, 2, 10, 100], default="foo"
            ... ).convert_to.list()
            [(3, 10), ('foo', 100)]

            A key function may also be applied to each item to use during comparisons:

            >>> BaseIterChain(["apples", "bananas"]).diff(
            ...     ["Apples", "Oranges"], key=str.lower
            ... ).convert_to.list()
            [('bananas', 'Oranges')]
        """
        return self.into(
            f=ft.partial(diff_with, others=others, default=default, key=key)
        )

    def partition(self, n: int, pad: V | None = None) -> "IterChain[tuple[V, ...]]":
        """
        Partitions into chunks of size n, padding last if needed (see cytoolz.partition).

        Example:
            >>> BaseIterChain([1, 2, 3, 4, 5]).partition(2, pad=0).convert_to.list()
            [(1, 2), (3, 4), (5, 0)]
        """
        return self.into(f=ft.partial(cz.itertoolz.partition, n, pad=pad))

    def partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        """
        Partitions into chunks of size n, last chunk may be smaller (see cytoolz.partition_all).

        Example:
            >>> BaseIterChain([1, 2, 3, 4, 5]).partition_all(2).convert_to.list()
            [(1, 2), (3, 4), (5,)]
        """
        return self.into(f=ft.partial(cz.itertoolz.partition_all, n))

    def rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        """
        Creates a sliding window of given length (see cytoolz.sliding_window).

        Example:
            >>> BaseIterChain([1, 2, 3, 4]).rolling(3).convert_to.list()
            [(1, 2, 3), (2, 3, 4)]
        """
        return self.into(f=ft.partial(cz.itertoolz.sliding_window, length))
