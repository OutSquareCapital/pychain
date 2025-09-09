import itertools
from collections.abc import Callable, Iterable
from functools import reduce
from random import Random
from typing import TYPE_CHECKING, Any, Concatenate, Literal, Self, overload

import cytoolz as cz

from pychain._dict import Dict

from ._core import Check, CommonBase, Process, Transform, dict_on, list_on, peek, peekn

if TYPE_CHECKING:
    from ._dict import Dict
    from ._list import List


class Iter[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]
    __slots__ = ("_data",)

    def transform[**P, U](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Iter[U]":
        return Iter(func(self._data, *args, **kwargs))

    @overload
    def combinations(self, r: Literal[2]) -> "Iter[tuple[T, T]]": ...
    @overload
    def combinations(self, r: Literal[3]) -> "Iter[tuple[T, T, T]]": ...
    @overload
    def combinations(self, r: Literal[4]) -> "Iter[tuple[T, T, T, T]]": ...
    @overload
    def combinations(self, r: Literal[5]) -> "Iter[tuple[T, T, T, T, T]]": ...
    def combinations(self, r: int) -> "Iter[tuple[T, ...]]":
        """Return all combinations of length r.

        Example:
            >>> Iter([1, 2, 3]).combinations(2).into_list()
            [(1, 2), (1, 3), (2, 3)]
        """
        return Iter(itertools.combinations(self._data, r))

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """Filter elements according to func and return a new Iterable wrapper.

        Example:
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).into_list()
            [2, 3]
        """
        return self._new(filter(func, self._data, *args, **kwargs))

    def take_while(self, predicate: Check[T]) -> Self:
        """Take items while predicate holds and return a new Iterable wrapper.

        Example:
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).into_list()
            [1, 2]
        """
        return self._new(itertools.takewhile(predicate, self._data))

    def drop_while(self, predicate: Check[T]) -> Self:
        """Drop items while predicate holds and return the remainder.

        Example:
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).into_list()
            [0]
        """
        return self._new(itertools.dropwhile(predicate, self._data))

    def interpose(self, element: T) -> Self:
        """Interpose element between items and return a new Iterable wrapper.

        Example:
            >>> Iter([1, 2]).interpose(0).into_list()
            [1, 0, 2]
        """
        return self._new(cz.itertoolz.interpose(element, self._data))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """Return the top-n items according to key.

        Example:
            >>> Iter([1, 3, 2]).top_n(2).into_list()
            [3, 2]
        """
        return self._new(cz.itertoolz.topk(n, self._data, key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """Randomly sample items with given probability.

        Example:
            >>> len(Iterable(Iter([1, 2, 3]).random_sample(0.5)))  # doctest: +SKIP
            1
        """
        return self._new(cz.itertoolz.random_sample(probability, self._data, state))

    def accumulate(self, f: Callable[[T, T], T]) -> Self:
        """Return cumulative application of binary op f.

        Example:
            >>> Iter([1, 2, 3]).accumulate(lambda a, b: a + b).into_list()
            [1, 3, 6]
        """
        return self._new(cz.itertoolz.accumulate(f, self._data))

    def insert_left(self, value: T) -> Self:
        """Prepend value to the sequence and return a new Iterable wrapper.

        Example:
            >>> Iter([2, 3]).insert_left(1).into_list()
            [1, 2, 3]
        """
        return self._new(cz.itertoolz.cons(value, self._data))

    def peekn(self, n: int, note: str | None = None) -> Self:
        """Print and return sequence after peeking n items.

        Example:
            >>> Iter([1, 2, 3]).peekn(2).into_list()
            Peeked 2 values: [1, 2]
            [1, 2, 3]
        """
        return self._new(peekn(self._data, n, note))

    def peek(self, note: str | None = None) -> Self:
        """Print and return sequence after peeking first item.

        Example:
            >>> Iter([1, 2]).peek().into_list()
            Peeked value: 1
            [1, 2]
        """
        return self._new(peek(self._data, note))

    def head(self, n: int) -> Self:
        """Return first n elements wrapped.

        Example:
            >>> Iter([1, 2, 3]).head(2).into_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        """Return last n elements wrapped.

        Example:
            >>> Iter([1, 2, 3]).tail(2).into_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        """Drop first n elements and return the remainder wrapped.

        Example:
            >>> Iter([1, 2, 3]).drop_first(1).into_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.drop(n, self._data))

    def every(self, index: int) -> Self:
        """Return every nth item starting from first.

        Example:
            >>> Iter([10, 20, 30, 40]).every(2).into_list()
            [10, 30]
        """
        return self._new(cz.itertoolz.take_nth(index, self._data))

    def unique(self) -> Self:
        """Return unique items preserving order.

        Example:
            >>> Iter([1, 2, 1]).unique().into_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.unique(self._data))

    def merge_sorted(
        self, *others: Iterable[T], sort_on: Callable[[T], Any] | None = None
    ) -> Self:
        """Merge already-sorted sequences.

        Example:
            >>> Iter([1, 3]).merge_sorted([2, 4]).into_list()
            [1, 2, 3, 4]
        """
        return self._new(cz.itertoolz.merge_sorted(self._data, *others, key=sort_on))

    def interleave(self, *others: Iterable[T]) -> Self:
        """Interleave multiple sequences element-wise.

        Example:
            >>> Iter([1, 2]).interleave([3, 4]).into_list()
            [1, 3, 2, 4]
        """
        return self._new(cz.itertoolz.interleave((self._data, *others)))

    def concat(self, *others: Iterable[T]) -> Self:
        """Concatenate multiple sequences.

        Example:
            >>> Iter([1]).concat([2, 3]).into_list()
            [1, 2, 3]
        """
        return self._new(cz.itertoolz.concat((self._data, *others)))

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce the sequence using func.

        Example:
            >>> Iter([1, 2, 3]).reduce(lambda a, b: a + b)
            6
        """
        return reduce(func, self._data)

    def is_distinct(self) -> bool:
        """Return True if all items are distinct.

        Example:
            >>> Iter([1, 2]).is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """Return True if all items are truthy.

        Example:
            >>> Iter([1, True]).all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """Return True if any item is truthy.

        Example:
            >>> Iter([0, 1]).any()
            True
        """
        return any(self._data)

    def agg[**P](
        self,
        f: Callable[Concatenate[Iterable[T], P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Apply aggregator f to the whole Iterable and return result.

        Example:
            >>> Iter([1, 2]).agg(sum)
            3
        """
        return f(self._data, *args, **kwargs)

    def first(self) -> T:
        """Return the first element.

        Example:
            >>> Iter([9]).first()
            9
        """
        return cz.itertoolz.first(self._data)

    def second(self) -> T:
        """Return the second element.

        Example:
            >>> Iter([9, 8]).second()
            8
        """
        return cz.itertoolz.second(self._data)

    def last(self) -> T:
        """Return the last element.

        Example:
            >>> Iter([7, 8, 9]).last()
            9
        """
        return cz.itertoolz.last(self._data)

    def length(self) -> int:
        """Return the length of the sequence.

        Example:
            >>> Iter([1, 2]).length()
            2
        """
        return cz.itertoolz.count(self._data)

    def at_index(self, index: int) -> T:
        """Return item at index.

        Example:
            >>> Iter([10, 20]).at_index(1)
            20
        """
        return cz.itertoolz.nth(index, self._data)

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ) -> "Iter[R]":
        """Map each element through func and return a Iter of results.

        Example:
            >>> Iter([1, 2]).map(lambda x: x + 1).into_list()
            [2, 3]
        """
        return Iter(map(func, self._data, *args, **kwargs))

    def flatten(self: "Iter[Iterable[Any]]") -> "Iter[T]":
        """Flatten one level of nesting and return a new Iterable wrapper.

        Example:
            >>> Iter([[1, 2], [3]]).flatten().into_list()
            [1, 2, 3]
        """
        return Iter(cz.itertoolz.concat(self._data))

    def flat_map[R, **P](
        self,
        func: Callable[Concatenate[T, P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Iter[R]":
        """Maps a function over a sequence and flattens the result by one level.

        It applies a function to each element, where the function must return
        an iterable. The resulting iterables are then chained together into a
        single, "flat" sequence.

        It's an efficient shortcut for `.map(func).flatten()`.

        Example:
            >>> # For each author, get a list of their books.
            >>> authors = Iter(["author_A", "author_B"])
            >>> def get_books(author_id):
            ...     # This could be an API call that returns a list of books
            ...     return [f"{author_id}_book1", f"{author_id}_book2"]
            >>>
            >>> authors.flat_map(get_books).into_list()
            ['author_A_book1', 'author_A_book2', 'author_B_book1', 'author_B_book2']
        """
        return Iter(cz.itertoolz.concat(map(func, self._data, *args, **kwargs)))

    def enumerate(self) -> "Iter[tuple[int, T]]":
        """Return a Iter of (index, value) pairs.

        Example:
            >>> Iter(["a", "b"]).enumerate().into_list()
            [(0, 'a'), (1, 'b')]
        """
        return Iter(enumerate(self._data))

    def batch(self, n: int) -> "Iter[tuple[T, ...]]":
        """Batch elements into tuples of length n and return a new Iter.

        Example:
            >>> Iter("ABCDEFG").batch(3).into_list()
            [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
        """
        return Iter(itertools.batched(self._data, n))

    def starmap[U: Iterable[Any], R](
        self: "Iter[U]", func: Callable[..., R]
    ) -> "Iter[R]":
        """Applies a function to each element, where each element is an iterable.

        Unlike `.map()`, which passes each element as a single argument,
        `.starmap()` unpacks each element into positional arguments for the function.

        In short, for each `element` in the sequence, it computes `func(*element)`.

        **Tip**:
            It is the perfect tool to process pairs generated by `.product()`
            or `.zip_with()`.

        Example:
            >>> colors = Iter(["blue", "red"])
            >>> sizes = ["S", "M"]
            >>>
            >>> def make_sku(color, size):
            ...     return f"{color}-{size}"
            >>>
            >>> colors.product(sizes).starmap(make_sku).into_list()
            ['blue-S', 'blue-M', 'red-S', 'red-M']
        """
        return Iter(itertools.starmap(func, self._data))

    def partition(self, n: int, pad: T | None = None) -> "Iter[tuple[T, ...]]":
        """Partition into tuples of length n, optionally padded.

        Example:
            >>> Iter([1, 2, 3, 4]).partition(2).into_list()
            [(1, 2), (3, 4)]
        """
        return Iter(cz.itertoolz.partition(n, self._data, pad))

    def partition_all(self, n: int) -> "Iter[tuple[T, ...]]":
        """Partition into tuples of length at most n.

        Example:
            >>> Iter([1, 2, 3]).partition_all(2).into_list()
            [(1, 2), (3,)]
        """
        return Iter(cz.itertoolz.partition_all(n, self._data))

    def rolling(self, length: int) -> "Iter[tuple[T, ...]]":
        """Return sliding windows of the given length.

        Example:
            >>> Iter([1, 2, 3]).rolling(2).into_list()
            [(1, 2), (2, 3)]
        """
        return Iter(cz.itertoolz.sliding_window(length, self._data))

    def product(self, other: Iterable[T]) -> "Iter[tuple[T, T]]":
        """Computes the Cartesian product with another iterable.

        This is the declarative equivalent of nested for-loops. It pairs
        every element from the source iterable with every element from the
        other iterable.

        **Tip**:
            This method is often chained with `.starmap()` to apply a
            function to each generated pair.

        Example:
            >>> colors = Iter(["blue", "red"])
            >>> sizes = ["S", "M"]
            >>> colors.product(sizes).into_list()
            [('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
        """

        return Iter(itertools.product(self._data, other))

    def repeat(self, n: int) -> "Iter[Iterable[T]]":
        """Repeat the entire iterable n times (as elements) and return Iter.

        Example:
            >>> Iter([1, 2]).repeat(2).into_list()
            [[1, 2], [1, 2]]
        """
        return Iter(itertools.repeat(self._data, n))

    def diff(
        self,
        *others: Iterable[T],
        key: Process[T] | None = None,
    ) -> "Iter[tuple[T, ...]]":
        """Yield differences between sequences.

        Example:
            >>> Iter([1, 2, 3]).diff([1, 2, 10]).into_list()
            [(3, 10)]
        """
        return Iter(cz.itertoolz.diff(self._data, *others, ccpdefault=None, key=key))

    def zip_with(
        self, *others: Iterable[T], strict: bool = False
    ) -> "Iter[tuple[T, ...]]":
        """Zip with other iterables, optionally strict, wrapped in Iter.

        Example:
            >>> Iter([1, 2]).zip_with([10, 20]).into_list()
            [(1, 10), (2, 20)]
        """
        return Iter(zip(self._data, *others, strict=strict))

    def reduce_by[K](
        self, key: Transform[T, K], binop: Callable[[T, T], T]
    ) -> "Iter[K]":
        """Perform a simultaneous groupby and reduction
        on the elements of the sequence.

        Example:
            >>> Iter([1, 2, 3, 4]).reduce_by(
            ...     key=lambda x: x % 2, binop=lambda a, b: a + b
            ... ).into_list()
            [1, 0]
        """

        return Iter(cz.itertoolz.reduceby(key, binop, self._data))

    def group_by[K](self, on: Transform[T, K]) -> "Dict[K, list[T]]":
        """Group elements by key function and return a Dict result.

        Example:
            >>> Iter(["a", "bb"]).group_by(len)
            {1: ['a'], 2: ['bb']}
        """
        return dict_on(cz.itertoolz.groupby(on, self._data))

    def frequencies(self) -> "Dict[T, int]":
        """Return a Dict of value frequencies.

        Example:
            >>> Iter([1, 1, 2]).frequencies()
            {1: 2, 2: 1}
        """
        return dict_on(cz.itertoolz.frequencies(self._data))

    def into_list(self) -> "List[T]":
        """Return a List wrapping the elements of the iterable.

        Example:
            >>> Iter([1, 2, 3]).into_list()
            [1, 2, 3]
        """
        return list_on(list(self._data))
