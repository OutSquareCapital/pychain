import functools
import itertools
import statistics
from collections import deque
from collections.abc import Callable, Iterable
from random import Random
from typing import TYPE_CHECKING, Any, Concatenate, Literal, Self, overload

import cytoolz as cz

from . import _core as core

if TYPE_CHECKING:
    from ._dict import Dict
    from ._sequence import SeqMut


class Iter[T](core.CommonBase[Iterable[T]]):
    _data: Iterable[T]
    __slots__ = ("_data",)

    def pipe[**P, U](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Iter[U]":
        return Iter(func(self._data, *args, **kwargs))

    def to_list(self) -> "SeqMut[T]":
        """Return a SeqMut wrapping the elements of the iterable.

        **Example:**
            >>> Iter([1, 2, 3]).to_list()
            [1, 2, 3]
        """
        return core.mut_seq_factory(list(self._data))

    def to_deque(self, maxlen: int | None = None) -> "SeqMut[T]":
        """Return a SeqMut wrapping the elements of the iterable.

        **Example:**
            >>> Iter([1, 2, 3]).to_deque()
            deque([1, 2, 3])
        """
        return core.mut_seq_factory(deque(self._data, maxlen))

    # CONSTRUCTORS------------------------------------------------------------------

    @classmethod
    def from_count(cls, start: int = 0, step: int = 1) -> "Iter[int]":
        """Create an infinite iterator of evenly spaced values.

        This is a class method that acts as a constructor.

        Warning: This creates an infinite iterator. Be sure to use .head() or
        .slice() to limit the number of items taken.

        **Example:**
            >>> Iter.from_count(10, 2).head(3).to_list()
            [10, 12, 14]
        """
        return cls.__call__(itertools.count(start, step))

    @classmethod
    def from_range(cls, start: int, stop: int, step: int = 1) -> "Iter[int]":
        """Create an iterator from a range.
        **Example:**
            >>> Iter.from_range(1, 5).to_list()
            [1, 2, 3, 4]
        """
        return Iter(range(start, stop, step))

    @classmethod
    def from_elements[U](cls, *elements: U) -> "Iter[U]":
        """Create an Iter from a sequence of elements.

        This is a class method that acts as a constructor from unpacked arguments.

        **Example:**
            >>> Iter.from_elements(1, 2, 3).to_list()
            [1, 2, 3]
        """
        return Iter(elements)

    @classmethod
    def from_func[U](cls, func: core.Process[U], n: U) -> "Iter[U]":
        """Create an infinite iterator by repeatedly applying a function.

        **Example:**
            >>> Iter.from_func(lambda x: x + 1, 0).head(3).to_list()
            [0, 1, 2]
        """
        return Iter(cz.itertoolz.iterate(func, n))

    # BUILTINS------------------------------------------------------------------

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ) -> "Iter[R]":
        """Map each element through func and return a Iter of results.

        **Example:**
            >>> Iter([1, 2]).map(lambda x: x + 1).to_list()
            [2, 3]
        """
        return Iter(map(func, self._data, *args, **kwargs))

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """Filter elements according to func and return a new Iterable wrapper.

        **Example:**
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).to_list()
            [2, 3]
        """
        return self._new(filter(func, self._data, *args, **kwargs))

    def filter_false[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """Return elements for which func is false.

        **Example:**
            >>> Iter([1, 2, 3]).filter_false(lambda x: x > 1).to_list()
            [1]
        """
        return self._new(itertools.filterfalse(func, self._data, *args, **kwargs))

    @overload
    def zip[T1](
        self, iter1: Iterable[T1], /, *, strict: bool = ...
    ) -> "Iter[tuple[T, T1]]": ...
    @overload
    def zip[T1, T2](
        self, iter1: Iterable[T1], iter2: Iterable[T2], /, *, strict: bool = ...
    ) -> "Iter[tuple[T, T1, T2]]": ...
    @overload
    def zip[T1, T2, T3](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        /,
        *,
        strict: bool = ...,
    ) -> "Iter[tuple[T, T1, T2, T3]]": ...
    @overload
    def zip[T1, T2, T3, T4](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        /,
        *,
        strict: bool = ...,
    ) -> "Iter[tuple[T, T1, T2, T3, T4]]": ...
    @overload
    def zip[T1, T2, T3, T4, T5](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        /,
        *,
        strict: bool = ...,
    ) -> "Iter[tuple[T, T1, T2, T3, T4, T5]]": ...
    def zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> "Iter[tuple[Any, ...]]":
        """Zip with other iterables, optionally strict, wrapped in Iter.

        **Example:**
            >>> Iter([1, 2]).zip([10, 20]).to_list()
            [(1, 10), (2, 20)]
        """
        return Iter(zip(self._data, *others, strict=strict))

    def enumerate(self) -> "Iter[tuple[int, T]]":
        """Return a Iter of (index, value) pairs.

        **Example:**
            >>> Iter(["a", "b"]).enumerate().to_list()
            [(0, 'a'), (1, 'b')]
        """
        return Iter(enumerate(self._data))

    def sort[U: core.SupportsRichComparison[Any]](
        self: "Iter[U]",
        key: core.Transform[U, U] | None = None,
        reverse: bool = False,
    ) -> "Iter[U]":
        """Sort the elements of the sequence.

        Note: This method must consume the entire iterable to perform the sort.
        The result is a new iterable over the sorted sequence.

        Example:
            >>> Iter([3, 1, 2]).sort().to_list()
            [1, 2, 3]
            >>> data = Iter([{"age": 30}, {"age": 20}])
            >>> data.sort(key=lambda x: x["age"]).to_list()
            [{'age': 20}, {'age': 30}]
        """
        return self._new(sorted(self._data, key=key, reverse=reverse))

    # ITERTOOLS------------------------------------------------------------------

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

        **Example:**
            >>> Iter([1, 2, 3]).combinations(2).to_list()
            [(1, 2), (1, 3), (2, 3)]
        """
        return Iter(itertools.combinations(self._data, r))

    def batch(self, n: int) -> "Iter[tuple[T, ...]]":
        """Batch elements into tuples of length n and return a new Iter.

        **Example:**
            >>> Iter("ABCDEFG").batch(3).to_list()
            [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
        """
        return Iter(itertools.batched(self._data, n))

    def zip_longest[U](
        self, *others: Iterable[T], fill_value: U = None
    ) -> "Iter[tuple[U | T, ...]]":
        """Zip with other iterables, filling missing values.

        **Example:**
            >>> Iter([1, 2]).zip_longest([10], fill_value=0).to_list()
            [(1, 10), (2, 0)]
        """
        return Iter(itertools.zip_longest(self._data, *others, fillvalue=fill_value))

    def permutations(self, r: int | None = None) -> "Iter[tuple[T, ...]]":
        """Return all permutations of length r.

        **Example:**
            >>> Iter([1, 2, 3]).permutations(2).to_list()
            [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
        """
        return Iter(itertools.permutations(self._data, r))

    def compress(self, *selectors: bool) -> Self:
        """Filter elements using a boolean selector iterable.

        **Example:**
            >>> Iter("ABCDEF").compress(1, 0, 1, 0, 1, 1).to_list()
            ['A', 'C', 'E', 'F']
        """
        return self._new(itertools.compress(self._data, selectors))

    def take_while(self, predicate: core.Check[T]) -> Self:
        """Take items while predicate holds and return a new Iterable wrapper.

        **Example:**
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).to_list()
            [1, 2]
        """
        return self._new(itertools.takewhile(predicate, self._data))

    def drop_while(self, predicate: core.Check[T]) -> Self:
        """Drop items while predicate holds and return the remainder.

        **Example:**
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).to_list()
            [0]
        """
        return self._new(itertools.dropwhile(predicate, self._data))

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

        **Example:**
            >>> colors = Iter(["blue", "red"])
            >>> sizes = ["S", "M"]
            >>>
            >>> def make_sku(color, size):
            ...     return f"{color}-{size}"
            >>>
            >>> colors.product(sizes).starmap(make_sku).to_list()
            ['blue-S', 'blue-M', 'red-S', 'red-M']
        """
        return Iter(itertools.starmap(func, self._data))

    def product[U](self, other: Iterable[U]) -> "Iter[tuple[T, U]]":
        """Computes the Cartesian product with another iterable.

        This is the declarative equivalent of nested for-loops. It pairs
        every element from the source iterable with every element from the
        other iterable.

        **Tip**:
            This method is often chained with `.starmap()` to apply a
            function to each generated pair.

        **Example:**
            >>> colors = Iter(["blue", "red"])
            >>> sizes = ["S", "M"]
            >>> colors.product(sizes).to_list()
            [('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
        """

        return Iter(itertools.product(self._data, other))

    def combinations_with_replacement(self, r: int) -> "Iter[tuple[T, ...]]":
        """Return all combinations with replacement of length r.

        **Example:**
            >>> Iter([1, 2, 3]).combinations_with_replacement(2).to_list()
            [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
        """
        return Iter(itertools.combinations_with_replacement(self._data, r))

    def pairwise(self) -> "Iter[tuple[T, T]]":
        """Return an iterator over pairs of consecutive elements.

        **Example:**
            >>> Iter([1, 2, 3]).pairwise().to_list()
            [(1, 2), (2, 3)]
        """
        return Iter(itertools.pairwise(self._data))

    def slice(self, start: int, stop: int) -> "Iter[T]":
        """Return a slice of the iterable.

        **Example:**
            >>> Iter([1, 2, 3, 4, 5]).slice(1, 4).to_list()
            [2, 3, 4]
        """
        return Iter(itertools.islice(self._data, start, stop))

    def repeat(self, n: int) -> "Iter[Iterable[T]]":
        """Repeat the entire iterable n times (as elements) and return Iter.

        **Example:**
            >>> Iter([1, 2]).repeat(2).to_list()
            [[1, 2], [1, 2]]
        """
        return Iter(itertools.repeat(self._data, n))

    def cycle(self) -> Self:
        """Repeat the sequence indefinitely.

        Warning: This creates an infinite iterator. Be sure to use .head() or
        .slice() to limit the number of items taken.

        **Example:**
            >>> Iter([1, 2]).cycle().head(5).to_list()
            [1, 2, 1, 2, 1]
        """
        return self._new(itertools.cycle(self._data))

    # CYTOOLZ------------------------------------------------------------------

    def join[R, K](
        self,
        other: Iterable[R],
        left_on: core.Transform[T, K],
        right_on: core.Transform[R, K],
        left_default: T | None = None,
        right_default: R | None = None,
    ) -> "Iter[tuple[T, R]]":
        """Perform a relational join with another iterable.

        **Example:**
            >>> colors = Iter(["blue", "red"])
            >>> sizes = ["S", "M"]
            >>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).to_list()
            [(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
        """
        return Iter(
            cz.itertoolz.join(
                left_on, self._data, right_on, other, left_default, right_default
            )
        )

    def juxt[R](self, *funcs: core.Transform[T, R]) -> "Iter[tuple[R, ...]]":
        """Apply several functions to each item.

        Returns a new Iter where each item is a tuple of the results of
        applying each function to the original item.

        **Example:**
            >>> def is_even(n):
            ...     return n % 2 == 0
            >>> def is_positive(n):
            ...     return n > 0
            >>> Iter([1, -2, 3]).juxt(is_even, is_positive).to_list()
            [(False, True), (True, False), (False, True)]
        """
        return self.map(cz.functoolz.juxt(*funcs))

    def interpose(self, element: T) -> Self:
        """Interpose element between items and return a new Iterable wrapper.

        **Example:**
            >>> Iter([1, 2]).interpose(0).to_list()
            [1, 0, 2]
        """
        return self._new(cz.itertoolz.interpose(element, self._data))

    def top_n(self, n: int, key: core.Transform[T, Any] | None = None) -> Self:
        """Return the top-n items according to key.

        **Example:**
            >>> Iter([1, 3, 2]).top_n(2).to_list()
            [3, 2]
        """
        return self._new(cz.itertoolz.topk(n, self._data, key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """Randomly sample items with given probability.

        **Example:**
            >>> len(Iterable(Iter([1, 2, 3]).random_sample(0.5)))  # doctest: +SKIP
            1
        """
        return self._new(cz.itertoolz.random_sample(probability, self._data, state))

    def accumulate(self, f: Callable[[T, T], T]) -> Self:
        """Return cumulative application of binary op f.

        **Example:**
            >>> Iter([1, 2, 3]).accumulate(lambda a, b: a + b).to_list()
            [1, 3, 6]
        """
        return self._new(cz.itertoolz.accumulate(f, self._data))

    def insert_left(self, value: T) -> Self:
        """Prepend value to the sequence and return a new Iterable wrapper.

        **Example:**
            >>> Iter([2, 3]).insert_left(1).to_list()
            [1, 2, 3]
        """
        return self._new(cz.itertoolz.cons(value, self._data))

    def peekn(self, n: int) -> Self:
        """Print and return sequence after peeking n items.

        **Example:**
            >>> Iter([1, 2, 3]).peekn(2).to_list()
            Peeked 2 values: (1, 2)
            [1, 2, 3]
        """

        def _():
            peeked = core.Peeked(*cz.itertoolz.peekn(n, self._data))
            print(f"Peeked {n} values: {peeked.value}")
            return peeked.sequence

        return self._new(_())

    def peek(self) -> Self:
        """Print and return sequence after peeking first item.

        **Example:**
            >>> Iter([1, 2]).peek().to_list()
            Peeked value: 1
            [1, 2]
        """

        def _():
            peeked = core.Peeked(*cz.itertoolz.peek(self._data))
            print(f"Peeked value: {peeked.value}")
            return peeked.sequence

        return self._new(_())

    def head(self, n: int) -> Self:
        """Return first n elements wrapped.

        **Example:**
            >>> Iter([1, 2, 3]).head(2).to_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        """Return last n elements wrapped.

        **Example:**
            >>> Iter([1, 2, 3]).tail(2).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        """Drop first n elements and return the remainder wrapped.

        **Example:**
            >>> Iter([1, 2, 3]).drop_first(1).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.drop(n, self._data))

    def every(self, index: int) -> Self:
        """Return every nth item starting from first.

        **Example:**
            >>> Iter([10, 20, 30, 40]).every(2).to_list()
            [10, 30]
        """
        return self._new(cz.itertoolz.take_nth(index, self._data))

    def unique(self) -> Self:
        """Return unique items preserving order.

        **Example:**
            >>> Iter([1, 2, 1]).unique().to_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.unique(self._data))

    def merge_sorted(
        self, *others: Iterable[T], sort_on: core.Transform[T, Any] | None = None
    ) -> Self:
        """Merge already-sorted sequences.

        **Example:**
            >>> Iter([1, 3]).merge_sorted([2, 4]).to_list()
            [1, 2, 3, 4]
        """
        return self._new(cz.itertoolz.merge_sorted(self._data, *others, key=sort_on))

    def interleave(self, *others: Iterable[T]) -> Self:
        """Interleave multiple sequences element-wise.

        **Example:**
            >>> Iter([1, 2]).interleave([3, 4]).to_list()
            [1, 3, 2, 4]
        """
        return self._new(cz.itertoolz.interleave((self._data, *others)))

    def concat(self, *others: Iterable[T]) -> Self:
        """Concatenate multiple sequences.

        **Example:**
            >>> Iter([1]).concat([2, 3]).to_list()
            [1, 2, 3]
        """
        return self._new(cz.itertoolz.concat((self._data, *others)))

    def flatten[U](self: "Iter[Iterable[U]]") -> "Iter[U]":
        """Flatten one level of nesting and return a new Iterable wrapper.

        **Example:**
            >>> Iter([[1, 2], [3]]).flatten().to_list()
            [1, 2, 3]
        """
        return Iter(cz.itertoolz.concat(self._data))

    def map_flat[R, **P](
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

        **Example:**
            >>> # For each author, get a list of their books.
            >>> authors = Iter(["author_A", "author_B"])
            >>> def get_books(author_id):
            ...     # This could be an API call that returns a list of books
            ...     return [f"{author_id}_book1", f"{author_id}_book2"]
            >>>
            >>> authors.map_flat(get_books).to_list()
            ['author_A_book1', 'author_A_book2', 'author_B_book1', 'author_B_book2']
        """
        return Iter(cz.itertoolz.concat(map(func, self._data, *args, **kwargs)))

    def map_concat[R](
        self,
        func: core.Transform[Iterable[T], Iterable[R]],
        *others: Iterable[T],
    ) -> "Iter[R]":
        """Map and concatenate the results of applying a function to each
        element of the input iterables.

        **Example**:
            >>> Iter(["a", "b"]).map_concat(
            ...     lambda s: [c.upper() for c in s], ["c", "d", "e"]
            ... ).to_list()
            ['A', 'B', 'C', 'D', 'E']
        """
        return Iter(cz.itertoolz.mapcat(func, (self._data, *others)))

    def pluck[K, V](self: "Iter[core.Pluckable[K, V]]", key: K) -> "Iter[V]":
        """Extract a value from each element in the sequence using a key or index.

        This is a shortcut for `.map(lambda x: x[key])`.

        **Example:**
            >>> data = Iter([{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
            >>> data.pluck("val").to_list()
            ['a', 'b']

            >>> Iter([[10, 20], [30, 40]]).pluck(0).to_list()
            [10, 30]
        """
        return Iter(cz.itertoolz.pluck(key, self._data))

    def partition(self, n: int, pad: T | None = None) -> "Iter[tuple[T, ...]]":
        """Partition into tuples of length n, optionally padded.

        **Example:**
            >>> Iter([1, 2, 3, 4]).partition(2).to_list()
            [(1, 2), (3, 4)]
        """
        return Iter(cz.itertoolz.partition(n, self._data, pad))

    def partition_all(self, n: int) -> "Iter[tuple[T, ...]]":
        """Partition into tuples of length at most n.

        **Example:**
            >>> Iter([1, 2, 3]).partition_all(2).to_list()
            [(1, 2), (3,)]
        """
        return Iter(cz.itertoolz.partition_all(n, self._data))

    def rolling(self, length: int) -> "Iter[tuple[T, ...]]":
        """Return sliding windows of the given length.

        **Example:**
            >>> Iter([1, 2, 3]).rolling(2).to_list()
            [(1, 2), (2, 3)]
        """
        return Iter(cz.itertoolz.sliding_window(length, self._data))

    def diff(
        self,
        *others: Iterable[T],
        key: core.Process[T] | None = None,
    ) -> "Iter[tuple[T, ...]]":
        """Yield differences between sequences.

        **Example:**
            >>> Iter([1, 2, 3]).diff([1, 2, 10]).to_list()
            [(3, 10)]
        """
        return Iter(cz.itertoolz.diff(self._data, *others, ccpdefault=None, key=key))

    def reduce_by[K](
        self, key: core.Transform[T, K], binop: Callable[[T, T], T]
    ) -> "Iter[K]":
        """Perform a simultaneous groupby and reduction
        on the elements of the sequence.

        **Example:**
            >>> Iter([1, 2, 3, 4]).reduce_by(
            ...     key=lambda x: x % 2, binop=lambda a, b: a + b
            ... ).to_list()
            [1, 0]
        """

        return Iter(cz.itertoolz.reduceby(key, binop, self._data))

    def group_by[K](self, on: core.Transform[T, K]) -> "Dict[K, list[T]]":
        """Group elements by key function and return a Dict result.

        **Example:**
            >>> Iter(["a", "bb"]).group_by(len)
            {1: ['a'], 2: ['bb']}
        """
        return core.dict_factory(cz.itertoolz.groupby(on, self._data))

    def frequencies(self) -> "Dict[T, int]":
        """Return a Dict of value frequencies.

        **Example:**
            >>> Iter([1, 1, 2]).frequencies()
            {1: 2, 2: 1}
        """
        return core.dict_factory(cz.itertoolz.frequencies(self._data))

    # AGGREGATIONS------------------------------------------------------------------

    def sum[U: int | float](self: "Iter[U]") -> U | Literal[0]:
        """Return the sum of the sequence.

        **Example:**
            >>> Iter([1, 2, 3]).sum()
            6
        """
        return sum(self._data)

    def min[U: int | float](self: "Iter[U]") -> U:
        """Return the minimum value of the sequence.

        **Example:**
            >>> Iter([3, 1, 2]).min()
            1
        """
        return min(self._data)

    def max[U: int | float](self: "Iter[U]") -> U:
        """Return the maximum value of the sequence.

        **Example:**
            >>> Iter([3, 1, 2]).max()
            3
        """
        return max(self._data)

    def mean[U: int | float](self: "Iter[U]") -> float:
        """Return the mean of the sequence.

        **Example:**
            >>> Iter([1, 2, 3]).mean()
            2
        """
        return statistics.mean(self._data)

    def median[U: int | float](self: "Iter[U]") -> float:
        """Return the median of the sequence.

        **Example:**
            >>> Iter([1, 3, 2]).median()
            2
        """
        return statistics.median(self._data)

    def mode[U: int | float](self: "Iter[U]") -> U | Literal[0]:
        """Return the mode of the sequence.

        **Example:**
            >>> Iter([1, 2, 2, 3]).mode()
            2
        """
        return statistics.mode(self._data)

    def stdev[U: int | float](self: "Iter[U]") -> float | Literal[0]:
        """Return the standard deviation of the sequence.

        **Example:**
            >>> Iter([1, 2, 3]).stdev()
            1.0
        """
        return statistics.stdev(self._data)

    def variance[U: int | float](self: "Iter[U]") -> float | Literal[0]:
        """Return the variance of the sequence.

        **Example:**
            >>> Iter([1, 2, 3, 7, 8]).variance()
            9.7
        """
        return statistics.variance(self._data)

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce the sequence using func.

        **Example:**
            >>> Iter([1, 2, 3]).reduce(lambda a, b: a + b)
            6
        """
        return functools.reduce(func, self._data)

    def is_distinct(self) -> bool:
        """Return True if all items are distinct.

        **Example:**
            >>> Iter([1, 2]).is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """Return True if all items are truthy.

        **Example:**
            >>> Iter([1, True]).all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """Return True if any item is truthy.

        **Example:**
            >>> Iter([0, 1]).any()
            True
        """
        return any(self._data)

    def first(self) -> T:
        """Return the first element.

        **Example:**
            >>> Iter([9]).first()
            9
        """
        return cz.itertoolz.first(self._data)

    def second(self) -> T:
        """Return the second element.

        **Example:**
            >>> Iter([9, 8]).second()
            8
        """
        return cz.itertoolz.second(self._data)

    def last(self) -> T:
        """Return the last element.

        **Example:**
            >>> Iter([7, 8, 9]).last()
            9
        """
        return cz.itertoolz.last(self._data)

    def length(self) -> int:
        """Return the length of the sequence.

        **Example:**
            >>> Iter([1, 2]).length()
            2
        """
        return cz.itertoolz.count(self._data)

    def item(self, index: int) -> T:
        """Return item at index.

        **Example:**
            >>> Iter([10, 20]).item(1)
            20
        """
        return cz.itertoolz.nth(index, self._data)
