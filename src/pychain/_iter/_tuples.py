from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Literal, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class IterTuples[T](IterWrapper[T]):
    @overload
    def zip[T1](
        self, iter1: Iterable[T1], /, *, strict: bool = ...
    ) -> Iter[tuple[T, T1]]: ...
    @overload
    def zip[T1, T2](
        self, iter1: Iterable[T1], iter2: Iterable[T2], /, *, strict: bool = ...
    ) -> Iter[tuple[T, T1, T2]]: ...
    @overload
    def zip[T1, T2, T3](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        /,
        *,
        strict: bool = ...,
    ) -> Iter[tuple[T, T1, T2, T3]]: ...
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
    ) -> Iter[tuple[T, T1, T2, T3, T4]]: ...
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
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5]]: ...
    def zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> Iter[tuple[Any, ...]]:
        """
        Zip with other iterables, optionally strict.

        >>> from pychain import Iter
        >>> Iter([1, 2]).zip([10, 20]).into(list)
        [(1, 10), (2, 20)]
        """
        return self.pipe_into(zip, *others, strict=strict)

    def zip_offset[U](
        self,
        *others: Iterable[T],
        offsets: list[int],
        longest: bool = False,
        fillvalue: U = None,
    ) -> Iter[tuple[T | U, ...]]:
        """
        Zip the input iterables together, but offset the i-th iterable by the i-th item in offsets.

        >>> from pychain import Iter
        >>> Iter("0123").zip_offset("abcdef", offsets=(0, 1)).into(list)
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e')]

        This can be used as a lightweight alternative to SciPy or pandas to analyze data sets in which some series have a lead or lag relationship.

        By default, the sequence will end when the shortest iterable is exhausted.

        To continue until the longest iterable is exhausted, set longest to True.

        >>> Iter("0123").zip_offset("abcdef", offsets=(0, 1), longest=True).into(list)
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e'), (None, 'f')]
        """
        return self.pipe_into(
            lambda x: mit.zip_offset(
                x,
                *others,
                offsets=offsets,
                longest=longest,
                fillvalue=fillvalue,
            )
        )

    def zip_broadcast(
        self,
        *others: Iterable[T],
        scalar_types: tuple[type, type] | None = (str, bytes),
        strict: bool = False,
    ) -> Iter[tuple[T, ...]]:
        """
        Version of zip that "broadcasts" any scalar (i.e., non-iterable) items into output tuples.

        >>> from pychain import Iter
        >>> iterable_1 = [1, 2, 3]
        >>> iterable_2 = ["a", "b", "c"]
        >>> scalar = "_"
        >>> Iter(iterable_1).zip_broadcast(iterable_2, scalar).into(list)
        [(1, 'a', '_'), (2, 'b', '_'), (3, 'c', '_')]

        The scalar_types keyword argument determines what types are considered scalar.
        It is set to (str, bytes) by default. Set it to None to treat strings and byte strings as iterable:

        >>> Iter("abc").zip_broadcast(0, "xyz", scalar_types=None).into(list)
        [('a', 0, 'x'), ('b', 0, 'y'), ('c', 0, 'z')]

        If the strict keyword argument is True, then UnequalIterablesError will be raised if any of the iterables have different lengths.
        """

        return self.pipe_into(
            lambda x: mit.zip_broadcast(
                x, *others, scalar_types=scalar_types, strict=strict
            )
        )

    @overload
    def zip_equal(self) -> Iter[tuple[T]]: ...
    @overload
    def zip_equal[T2](self, __iter2: Iterable[T2]) -> Iter[tuple[T, T2]]: ...
    @overload
    def zip_equal[T2, T3](
        self, __iter2: Iterable[T2], __iter3: Iterable[T3]
    ) -> Iter[tuple[T, T2, T3]]: ...
    @overload
    def zip_equal[T2, T3, T4](
        self,
        __iter2: Iterable[T2],
        __iter3: Iterable[T3],
        __iter4: Iterable[T4],
    ) -> Iter[tuple[T, T2, T3, T4]]: ...
    @overload
    def zip_equal[T2, T3, T4, T5](
        self,
        __iter2: Iterable[T2],
        __iter3: Iterable[T3],
        __iter4: Iterable[T4],
        __iter5: Iterable[T5],
    ) -> Iter[tuple[T, T2, T3, T4, T5]]: ...
    @overload
    def zip_equal(
        __iter1: Iterable[Any],
        __iter2: Iterable[Any],
        __iter3: Iterable[Any],
        __iter4: Iterable[Any],
        __iter5: Iterable[Any],
        __iter6: Iterable[Any],
        *iterables: Iterable[Any],
    ) -> Iter[tuple[Any, ...]]: ...
    def zip_equal(self, *others: Iterable[Any]) -> Iter[tuple[Any, ...]]:
        return self.pipe_into(lambda x: mit.zip_equal(x, *others))

    def enumerate(self) -> Iter[tuple[int, T]]:
        """
        Return a Iter of (index, value) pairs.

        >>> from pychain import Iter
        >>> Iter(["a", "b"]).enumerate().into(list)
        [(0, 'a'), (1, 'b')]
        """
        return self.pipe_into(enumerate)

    @overload
    def combinations(self, r: Literal[2]) -> Iter[tuple[T, T]]: ...
    @overload
    def combinations(self, r: Literal[3]) -> Iter[tuple[T, T, T]]: ...
    @overload
    def combinations(self, r: Literal[4]) -> Iter[tuple[T, T, T, T]]: ...
    @overload
    def combinations(self, r: Literal[5]) -> Iter[tuple[T, T, T, T, T]]: ...
    def combinations(self, r: int) -> Iter[tuple[T, ...]]:
        """
        Return all combinations of length r.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).combinations(2).into(list)
        [(1, 2), (1, 3), (2, 3)]
        """
        return self.pipe_into(itertools.combinations, r)

    def batch(self, n: int) -> Iter[tuple[T, ...]]:
        """
        Batch elements into tuples of length n and return a new Iter.

        >>> from pychain import Iter
        >>> Iter("ABCDEFG").batch(3).into(list)
        [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
        """
        return self.pipe_into(itertools.batched, n)

    def zip_longest[U](
        self, *others: Iterable[T], fill_value: U = None
    ) -> Iter[tuple[U | T, ...]]:
        """
        Zip with other iterables, filling missing values.

        >>> from pychain import Iter
        >>> Iter([1, 2]).zip_longest([10], fill_value=0).into(list)
        [(1, 10), (2, 0)]
        """
        return self.pipe_into(itertools.zip_longest, *others, fillvalue=fill_value)

    def permutations(self, r: int | None = None) -> Iter[tuple[T, ...]]:
        """
        Return all permutations of length r.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).permutations(2).into(list)
        [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
        """
        return self.pipe_into(itertools.permutations, r)

    @overload
    def product(self) -> Iter[tuple[T]]: ...
    @overload
    def product[T1](self, iter1: Iterable[T1], /) -> Iter[tuple[T, T1]]: ...
    @overload
    def product[T1, T2](
        self, iter1: Iterable[T1], iter2: Iterable[T2], /
    ) -> Iter[tuple[T, T1, T2]]: ...
    @overload
    def product[T1, T2, T3](
        self, iter1: Iterable[T1], iter2: Iterable[T2], iter3: Iterable[T3], /
    ) -> Iter[tuple[T, T1, T2, T3]]: ...
    @overload
    def product[T1, T2, T3, T4](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4]]: ...
    @overload
    def product[T1, T2, T3, T4, T5](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5]]: ...
    @overload
    def product[T1, T2, T3, T4, T5, T6](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        iter6: Iterable[T6],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5, T6]]: ...
    @overload
    def product[T1, T2, T3, T4, T5, T6, T7](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        iter6: Iterable[T6],
        iter7: Iterable[T7],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5, T6, T7]]: ...
    @overload
    def product[T1, T2, T3, T4, T5, T6, T7, T8](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        iter6: Iterable[T6],
        iter7: Iterable[T7],
        iter8: Iterable[T8],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5, T6, T7, T8]]: ...
    @overload
    def product[T1, T2, T3, T4, T5, T6, T7, T8, T9](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        iter6: Iterable[T6],
        iter7: Iterable[T7],
        iter8: Iterable[T8],
        iter9: Iterable[T9],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5, T6, T7, T8, T9]]: ...
    @overload
    def product[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        iter5: Iterable[T5],
        iter6: Iterable[T6],
        iter7: Iterable[T7],
        iter8: Iterable[T8],
        iter9: Iterable[T9],
        iter10: Iterable[T10],
        /,
    ) -> Iter[tuple[T, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]: ...
    def product(self, *others: Iterable[Any]) -> Iter[tuple[Any, ...]]:
        """
        Computes the Cartesian product with another iterable.
        This is the declarative equivalent of nested for-loops.

        It pairs every element from the source iterable with every element from the
        other iterable.

        **Tip**: This method is often chained with `.starmap()` to apply a
        function to each generated pair.

        >>> from pychain import Iter
        >>> colors = Iter(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.product(sizes).into(list)
        [('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
        """
        return self.pipe_into(itertools.product, *others)

    def combinations_with_replacement(self, r: int) -> Iter[tuple[T, ...]]:
        """
        Return all combinations with replacement of length r.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).combinations_with_replacement(2).into(list)
        [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
        """
        return self.pipe_into(itertools.combinations_with_replacement, r)

    def pairwise(self) -> Iter[tuple[T, T]]:
        """
        Return an iterator over pairs of consecutive elements.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).pairwise().into(list)
        [(1, 2), (2, 3)]
        """
        return self.pipe_into(itertools.pairwise)

    def join[R, K](
        self,
        other: Iterable[R],
        left_on: Callable[[T], K],
        right_on: Callable[[R], K],
        left_default: T | None = None,
        right_default: R | None = None,
    ) -> Iter[tuple[T, R]]:
        """
        Perform a relational join with another iterable.

        >>> from pychain import Iter
        >>> colors = Iter(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).into(list)
        [(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
        """

        return self.pipe_into(
            lambda x: cz.itertoolz.join(
                leftkey=left_on,
                leftseq=x,
                rightkey=right_on,
                rightseq=other,
                left_default=left_default,
                right_default=right_default,
            )
        )

    def partition(self, n: int, pad: T | None = None) -> Iter[tuple[T, ...]]:
        """
        Partition sequence into tuples of length n

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4]).partition(2).into(list)
        [(1, 2), (3, 4)]

        If the length of seq is not evenly divisible by n, the final tuple is dropped if pad is not specified, or filled to length n by pad:

        >>> Iter([1, 2, 3, 4, 5]).partition(2).into(list)
        [(1, 2), (3, 4), (5, None)]
        """

        return self.pipe_into(partial(cz.itertoolz.partition, n, pad=pad))

    def partition_all(self, n: int) -> Iter[tuple[T, ...]]:
        """
        Partition all elements of sequence into tuples of length at most n

        The final tuple may be shorter to accommodate extra elements.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4]).partition_all(2).into(list)
        [(1, 2), (3, 4)]
        >>> Iter([1, 2, 3, 4, 5]).partition_all(2).into(list)
        [(1, 2), (3, 4), (5,)]
        """
        return self.pipe_into(partial(cz.itertoolz.partition_all, n))

    @overload
    def sliding_window(self, length: Literal[1]) -> Iter[tuple[T]]: ...
    @overload
    def sliding_window(self, length: Literal[2]) -> Iter[tuple[T, T]]: ...
    @overload
    def sliding_window(self, length: Literal[3]) -> Iter[tuple[T, T, T]]: ...
    @overload
    def sliding_window(self, length: Literal[4]) -> Iter[tuple[T, T, T, T]]: ...
    @overload
    def sliding_window(self, length: Literal[5]) -> Iter[tuple[T, T, T, T, T]]: ...
    @overload
    def sliding_window(self, length: Literal[6]) -> Iter[tuple[T, T, T, T, T, T]]: ...
    @overload
    def sliding_window(
        self, length: Literal[7]
    ) -> Iter[tuple[T, T, T, T, T, T, T]]: ...
    @overload
    def sliding_window(
        self, length: Literal[8]
    ) -> Iter[tuple[T, T, T, T, T, T, T, T]]: ...
    @overload
    def sliding_window(
        self, length: Literal[9]
    ) -> Iter[tuple[T, T, T, T, T, T, T, T, T]]: ...

    def sliding_window(self, length: int) -> Iter[tuple[T, ...]]:
        """
        A sequence of overlapping subsequences of the given length.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4]).sliding_window(2).into(list)
        [(1, 2), (2, 3), (3, 4)]

        This function allows you to apply custom function not available in the rolling namespace.


        >>> Iter([1, 2, 3, 4]).sliding_window(2).map(
        ...     lambda seq: float(sum(seq)) / len(seq)
        ... ).into(list)
        [1.5, 2.5, 3.5]
        """
        return self.pipe_into(partial(cz.itertoolz.sliding_window, length))

    def diff(
        self,
        *others: Iterable[T],
        default: T | None = None,
        key: Callable[[T], Any] | None = None,
    ) -> Iter[tuple[T, ...]]:
        """
        Return those items that differ between iterables.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).diff([1, 2, 10, 100], default=None).into(list)
        [(3, 10), (None, 100)]


        A key function may also be applied to each item to use during comparisons:

        >>> from pychain import Iter
        >>> Iter(["apples", "bananas"]).diff(["Apples", "Oranges"], key=str.lower).into(
        ...     list
        ... )
        [('bananas', 'Oranges')]
        """
        return self.pipe_into(cz.itertoolz.diff, *others, default=default, key=key)

    def adjacent(
        self, predicate: Callable[[T], bool], distance: int = 1
    ) -> Iter[tuple[bool, T]]:
        """
        Return an iterable over (bool, item) tuples.

        The output is a sequence of tuples where the item is drawn from iterable.

        The bool indicates whether that item satisfies the predicate or is adjacent to an item that does.

        For example, to find whether items are adjacent to a 3:

        >>> from pychain import Iter
        >>> Iter.from_range(0, 6).adjacent(lambda x: x == 3).into(list)
        [(False, 0), (False, 1), (True, 2), (True, 3), (True, 4), (False, 5)]

        Set distance to change what counts as adjacent. For example, to find whether items are two places away from a 3:

        >>> Iter.from_range(0, 6).adjacent(lambda x: x == 3, distance=2).into(list)
        [(False, 0), (True, 1), (True, 2), (True, 3), (True, 4), (True, 5)]

        This is useful for contextualizing the results of a search function.

        For example, a code comparison tool might want to identify lines that have changed, but also surrounding lines to give the viewer of the diff context.

        The predicate function will only be called once for each item in the iterable.

        See also groupby_transform, which can be used with this function to group ranges of items with the same bool value.
        """
        return self.pipe_into(lambda data: mit.adjacent(predicate, data, distance))

    def most_common(self, n: int | None = None) -> Iter[tuple[T, int]]:
        """
        Return an iterable over the n most common elements and their counts from the most common to the least.

        If n is None, then all elements are returned.

        >>> from pychain import Iter
        >>> Iter([1, 1, 2, 3, 3, 3]).most_common(2).into(list)
        [(3, 3), (1, 2)]
        """
        from collections import Counter

        return self.pipe_into(lambda data: Counter(data).most_common(n))

    def classify_unique(self) -> Iter[tuple[T, bool, bool]]:
        """
        Classify each element in terms of its uniqueness.

        For each element in the input iterable, return a 3-tuple consisting of:

        - The element itself
        - False if the element is equal to the one preceding it in the input, True otherwise (i.e. the equivalent of unique_justseen)
        - False if this element has been seen anywhere in the input before, True otherwise (i.e. the equivalent of unique_everseen)

        >>> from pychain import Iter
        >>> Iter("otto").classify_unique().into(list)  # doctest: +NORMALIZE_WHITESPACE
        [('o', True,  True),
        ('t', True,  True),
        ('t', False, False),
        ('o', True,  False)]

        This function is analogous to unique_everseen and is subject to the same performance considerations.
        """
        return self.pipe_into(mit.classify_unique)

    @overload
    def map_juxt[R1, R2](
        self,
        func1: Callable[[T], R1],
        func2: Callable[[T], R2],
        /,
    ) -> Iter[tuple[R1, R2]]: ...
    @overload
    def map_juxt[R, R1, R2, R3](
        self,
        func1: Callable[[T], R1],
        func2: Callable[[T], R2],
        func3: Callable[[T], R3],
        /,
    ) -> Iter[tuple[R1, R2, R3]]: ...
    @overload
    def map_juxt[R1, R2, R3, R4](
        self,
        func1: Callable[[T], R1],
        func2: Callable[[T], R2],
        func3: Callable[[T], R3],
        func4: Callable[[T], R4],
        /,
    ) -> Iter[tuple[R1, R2, R3, R4]]: ...

    def map_juxt(self, *funcs: Callable[[T], object]) -> Iter[tuple[object, ...]]:
        """
        Apply several functions to each item.

        Returns a new Iter where each item is a tuple of the results of applying each function to the original item.

        >>> from pychain import Iter
        >>> Iter([1, -2, 3]).map_juxt(lambda n: n % 2 == 0, lambda n: n > 0).into(list)
        [(False, True), (True, False), (False, True)]
        """
        return self.pipe_into(partial(map, cz.functoolz.juxt(*funcs)))

    def partition_by(self, predicate: Callable[[T], bool]) -> Iter[tuple[T, ...]]:
        """
        Partition the `iterable` into a sequence of `tuples` according to a predicate function.

        Every time the output of `predicate` changes, a new `tuple` is started,
        and subsequent items are collected into that `tuple`.

        >>> from pychain import Iter
        >>> Iter("I have space").partition_by(lambda c: c == " ").into(list)
        [('I',), (' ',), ('h', 'a', 'v', 'e'), (' ',), ('s', 'p', 'a', 'c', 'e')]

        >>> data = [1, 2, 1, 99, 88, 33, 99, -1, 5]
        >>> Iter(data).partition_by(lambda x: x > 10).into(list)
        [(1, 2, 1), (99, 88, 33, 99), (-1, 5)]

        """
        return self.pipe_into(partial(cz.recipes.partitionby, predicate))
