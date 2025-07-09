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
    """
    BaseIterChain provides a fluent interface for chaining transformations on iterables.
    Inspired by cytoolz, it enables functional-style data processing with immutable pipelines.

    Example:
        >>> chain = BaseIterChain([1, 2, 3, 4])
        >>> result = (
        ...     chain.filter(lambda x: x % 2 == 0)
        ...     .map(lambda x: x * 10)
        ...     .convert_to.list()
        ... )
        >>> print(result)
        [20, 40]
    """

    _value: Iterable[V]

    @property
    def convert_to(self) -> Converter[V]:
        """
        Returns a Converter for the iterable, providing methods to convert to list, set, array, etc.

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.convert_to.list()
            [1, 2, 3]
        """
        return Converter(_value=self.unwrap())

    @property
    def check_if(self) -> Checker[V]:
        """
        Returns a Checker for the iterable, providing boolean checks like all, any, distinct, etc.

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.check_if.all()
            True
        """
        return Checker(_value=self.unwrap())

    def into[V1](self, f: TransformFunc[Iterable[V], Iterable[V1]]) -> "IterChain[V1]":
        """
        Transforms the iterable using the provided function, returning a new chain.

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.into(reversed).convert_to.list()
            [3, 2, 1]
        """
        return self.__class__(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def in_range(self, n: int):
        """
        Repeats each element in the iterable n times.

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.in_range(2).convert_to.list()
            [1, 1, 2, 2]
        """
        return self.flat_map(lambda x: (x for _ in range(n)))

    def take_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Takes elements while predicate is true (like itertools.takewhile).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 2])
            >>> chain.take_while(lambda x: x < 3).convert_to.list()
            [1, 2]
        """
        return self.do(f=ft.partial(it.takewhile, predicate))

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Drops elements while predicate is true (like itertools.dropwhile).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 2])
            >>> chain.drop_while(lambda x: x < 3).convert_to.list()
            [3, 2]
        """
        return self.do(f=ft.partial(it.dropwhile, predicate))

    def interleave(self, *others: Iterable[V]) -> Self:
        """
        Interleaves the iterable with other iterables (see cytoolz.interleave).

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.interleave([10, 20]).convert_to.list()
            [1, 10, 2, 20]
        """
        return self.do(f=ft.partial(interleave, others=others))

    def interpose(self, element: V) -> Self:
        """
        Inserts the given element between each pair of elements (see cytoolz.interpose).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.interpose(0).convert_to.list()
            [1, 0, 2, 0, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.interpose, el=element))

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        """
        Returns the top n elements based on the key (see cytoolz.topk).

        Example:
            >>> chain = BaseIterChain([1, 5, 3, 2])
            >>> chain.top_n(2).convert_to.list()
            [5, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.topk, k=n, key=key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly samples elements with given probability (see cytoolz.random_sample).

        Example:
            >>> chain = BaseIterChain(range(100))
            >>> len(chain.random_sample(0.1).convert_to.list())  # ~10
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
            >>> chain = BaseIterChain([1, 2])
            >>> chain.concat([3, 4]).convert_to.list()
            [1, 2, 3, 4]
        """
        return self.do(f=ft.partial(concat, others=others))

    def filter(self, f: CheckFunc[V]) -> Self:
        """
        Filters elements by predicate (like built-in filter).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.filter(lambda x: x > 1).convert_to.list()
            [2, 3]
        """
        return self.do(f=ft.partial(filter, f))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Accumulates values using binary function (see cytoolz.accumulate).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.accumulate(lambda x, y: x + y).convert_to.list()
            [1, 3, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, binop=f))

    def cons(self, value: V) -> Self:
        """
        Prepends a value (see cytoolz.cons).

        Example:
            >>> chain = BaseIterChain([2, 3])
            >>> chain.cons(1).convert_to.list()
            [1, 2, 3]
        """
        return self.do(f=ft.partial(cz.itertoolz.cons, el=value))

    def peek(self, note: str | None = None) -> Self:
        """
        Peeks at elements, printing them optionally with a note.

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.peek("step1").convert_to.list()
            step1: [1, 2, 3]
            [1, 2, 3]
        """
        return self.do(f=ft.partial(peek, note=note))

    def peekn(self, n: int, note: str | None = None) -> Self:
        """
        Peeks at first n elements, printing them optionally with a note.

        Example:
            >>> chain = BaseIterChain(range(10))
            >>> chain.peekn(3).convert_to.list()
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        return self.do(f=ft.partial(peekn, n=n, note=note))

    def head(self, n: int) -> Self:
        """
        Takes first n elements (see cytoolz.take).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4])
            >>> chain.head(2).convert_to.list()
            [1, 2]
        """
        return self.do(f=ft.partial(cz.itertoolz.take, n=n))

    def tail(self, n: int) -> Self:
        """
        Takes last n elements (see cytoolz.tail).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4])
            >>> chain.tail(2).convert_to.list()
            [3, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.tail, n=n))

    def drop_first(self, n: int) -> Self:
        """
        Drops first n elements (see cytoolz.drop).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4])
            >>> chain.drop_first(2).convert_to.list()
            [3, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.drop, n=n))

    def every(self, index: int) -> Self:
        """
        Takes every index-th element (see cytoolz.take_nth).

        Example:
            >>> chain = BaseIterChain([0, 1, 2, 3, 4])
            >>> chain.every(2).convert_to.list()
            [0, 2, 4]
        """
        return self.do(f=ft.partial(cz.itertoolz.take_nth, n=index))

    def repeat(self, n: int) -> Self:
        """
        Repeats the iterable n times (see cytoolz.repeat).

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.repeat(2).convert_to.list()
            [1, 2, 1, 2]
        """
        return self.do(f=ft.partial(repeat, n=n))

    def unique(self) -> Self:
        """
        Returns unique elements (see cytoolz.unique).

        Example:
            >>> chain = BaseIterChain([1, 2, 2, 3])
            >>> chain.unique().convert_to.list()
            [1, 2, 3]
        """
        return self.do(f=cz.itertoolz.unique)

    def cumsum(self) -> Self:
        """
        Computes cumulative sum (see cytoolz.accumulate with operator.add).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.cumsum().convert_to.list()
            [1, 3, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.add))

    def cumprod(self) -> Self:
        """
        Computes cumulative product (see cytoolz.accumulate with operator.mul).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.cumprod().convert_to.list()
            [1, 2, 6]
        """
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.mul))

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        """
        Merges and sorts with other iterables (see cytoolz.merge_sorted).

        Example:
            >>> chain = BaseIterChain([1, 3])
            >>> chain.merge_sorted([2, 4]).convert_to.list()
            [1, 2, 3, 4]
        """
        return self.do(f=ft.partial(merge_sorted, others=others, sort_on=sort_on))

    def tap(self, func: Callable[[V], None]) -> Self:
        """
        Applies a side-effect function to each element (see cytoolz.do/tap).

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.tap(print).convert_to.list()
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
            >>> chain = BaseIterChain([1, 2])
            >>> chain.zip([10, 20]).convert_to.list()
            [(1, 10), (2, 20)]
        """
        return self.into(f=ft.partial(zip_with, others=others, strict=strict))

    def enumerate(self) -> "IterChain[tuple[int, V]]":
        """
        Enumerates the iterable (like built-in enumerate).

        Example:
            >>> chain = BaseIterChain(["a", "b"])
            >>> chain.enumerate().convert_to.list()
            [(0, 'a'), (1, 'b')]
        """
        return self.into(f=enumerate)

    def map[V1](self, f: TransformFunc[V, V1]) -> "IterChain[V1]":
        """
        Maps a function over elements (like built-in map).

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.map(lambda x: x * 2).convert_to.list()
            [2, 4]
        """
        return self.into(f=ft.partial(map, f))

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "IterChain[V1]":
        """
        Maps a function and flattens the result (see cytoolz.concatmap).

        Example:
            >>> chain = BaseIterChain([1, 2])
            >>> chain.flat_map(lambda x: [x, x + 10]).convert_to.list()
            [1, 11, 2, 12]
        """
        return self.into(f=ft.partial(flat_map, func=f))

    def flatten(self) -> "IterChain[Any]":
        """
        Flattens nested iterables (see cytoolz.concat).

        Example:
            >>> chain = BaseIterChain([[1, 2], [3, 4]])
            >>> chain.flatten().convert_to.list()
            [1, 2, 3, 4]
        """
        return self.into(f=cz.itertoolz.concat)

    def diff(
        self,
        *others: Iterable[V],
        key: ProcessFunc[V] | None = None,
    ) -> "IterChain[tuple[V, ...]]":
        """
        Computes the difference with other iterables (see cytoolz.diff).

        Example:
            >>> chain = BaseIterChain([1, 2, 3])
            >>> chain.diff([2, 3, 4]).convert_to.list()
            [(1, 4)]
        """
        return self.into(f=ft.partial(diff_with, others=others, key=key))

    def partition(self, n: int, pad: V | None = None) -> "IterChain[tuple[V, ...]]":
        """
        Partitions into chunks of size n, padding last if needed (see cytoolz.partition).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4, 5])
            >>> chain.partition(2, pad=0).convert_to.list()
            [(1, 2), (3, 4), (5, 0)]
        """
        return self.into(f=ft.partial(cz.itertoolz.partition, n=n, pad=pad))

    def partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        """
        Partitions into chunks of size n, last chunk may be smaller (see cytoolz.partition_all).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4, 5])
            >>> chain.partition_all(2).convert_to.list()
            [(1, 2), (3, 4), (5,)]
        """
        return self.into(f=ft.partial(cz.itertoolz.partition_all, n=n))

    def rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        """
        Creates a sliding window of given length (see cytoolz.sliding_window).

        Example:
            >>> chain = BaseIterChain([1, 2, 3, 4])
            >>> chain.rolling(3).convert_to.list()
            [(1, 2, 3), (2, 3, 4)]
        """
        return self.into(f=ft.partial(cz.itertoolz.sliding_window, length))
