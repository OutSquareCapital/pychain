import itertools
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, Literal, overload

import cytoolz as cz
import more_itertools as mit

from .. import _core as core
from ._aggregations import IterAgg
from ._conversions import IterConvert
from ._process import IterProcess

if TYPE_CHECKING:
    pass


class Iter[T](IterAgg[T], IterProcess[T], IterConvert[T]):
    _data: Iterable[T]
    __slots__ = ("_data",)

    def pipe[**P, U](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Iter[U]":
        return Iter(func(self._data, *args, **kwargs))

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
        return Iter(itertools.count(start, step))

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

    # TRANSFORMATIONS------------------------------------------------------------------

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ) -> "Iter[R]":
        """Map each element through func and return a Iter of results.

        **Example:**
            >>> Iter([1, 2]).map(lambda x: x + 1).to_list()
            [2, 3]
        """
        return Iter(map(func, self._data, *args, **kwargs))

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
                leftkey=left_on,
                leftseq=self._data,
                rightkey=right_on,
                rightseq=other,
                left_default=left_default,
                right_default=right_default,
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

    def adjacent(
        self, predicate: core.Check[T], distance: int = 1
    ) -> "Iter[tuple[bool, T]]":
        return Iter(mit.adjacent(predicate, self._data, distance))

    def repeat(self, n: int) -> "Iter[Iterable[T]]":
        """Repeat the entire iterable n times (as elements) and return Iter.

        **Example:**
            >>> Iter([1, 2]).repeat(2).to_list()
            [[1, 2], [1, 2]]
        """
        return Iter(itertools.repeat(self._data, n))

    def flatten[U](self: "Iter[Iterable[U]]") -> "Iter[U]":
        """Flatten one level of nesting and return a new Iterable wrapper.

        **Example:**
            >>> Iter([[1, 2], [3]]).flatten().to_list()
            [1, 2, 3]
        """
        return Iter(cz.itertoolz.concat(self._data))

    # PROCESSING------------------------------------------------------------------

    def sort[U: core.SupportsRichComparison[Any]](
        self: "Iter[U]",
        key: core.Transform[U, Any] | None = None,
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
