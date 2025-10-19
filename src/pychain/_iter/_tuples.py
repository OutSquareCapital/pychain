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


class BaseTuples[T](IterWrapper[T]):
    @overload
    def zip[T1](
        self, iter1: Iterable[T1], /, *, strict: bool = ...
    ) -> Iter[tuple[T, T1]]: ...
    @overload
    def zip[T1, T2](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        /,
        *,
        strict: bool = ...,
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
    def zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> Iter[tuple[Any, ...]]:
        """
        Zip with other iterables, optionally strict.

        >>> import pychain as pc
        >>> pc.Iter([1, 2]).zip([10, 20]).into(list)
        [(1, 10), (2, 20)]
        """
        return self.apply(zip, *others, strict=strict)

    def zip_offset[U](
        self,
        *others: Iterable[T],
        offsets: list[int],
        longest: bool = False,
        fillvalue: U = None,
    ) -> Iter[tuple[T | U, ...]]:
        """
        Zip the input iterables together, but offset the i-th iterable by the i-th item in offsets.

        >>> import pychain as pc
        >>> pc.Iter("0123").zip_offset("abcdef", offsets=(0, 1)).into(list)
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e')]

        This can be used as a lightweight alternative to SciPy or pandas to analyze data sets in which some series have a lead or lag relationship.

        By default, the sequence will end when the shortest iterable is exhausted.

        To continue until the longest iterable is exhausted, set longest to True.

        >>> pc.Iter("0123").zip_offset("abcdef", offsets=(0, 1), longest=True).into(
        ...     list
        ... )
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e'), (None, 'f')]
        """
        return self.apply(
            lambda x: mit.zip_offset(
                x,
                *others,
                offsets=offsets,
                longest=longest,
                fillvalue=fillvalue,
            )
        )

    @overload
    def zip_broadcast[T1](
        self,
        iter1: Iterable[T1],
        /,
        *,
        strict: bool = False,
    ) -> Iter[tuple[T, T1]]: ...
    @overload
    def zip_broadcast[T1, T2](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        /,
        *,
        strict: bool = False,
    ) -> Iter[tuple[T, T1, T2]]: ...
    @overload
    def zip_broadcast[T1, T2, T3](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        /,
        *,
        strict: bool = False,
    ) -> Iter[tuple[T, T1, T2, T3]]: ...
    @overload
    def zip_broadcast[T1, T2, T3, T4](
        self,
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4],
        /,
        *,
        strict: bool = False,
    ) -> Iter[tuple[T, T1, T2, T3, T4]]: ...
    def zip_broadcast(
        self, *others: Iterable[Any], strict: bool = False
    ) -> Iter[tuple[Any, ...]]:
        """
        Version of zip that "broadcasts" any scalar (i.e., non-iterable) items into output tuples.
        str and bytes are not treated as iterables.

        >>> import pychain as pc
        >>> iterable_1 = [1, 2, 3]
        >>> iterable_2 = ["a", "b", "c"]
        >>> scalar = "_"
        >>> pc.Iter(iterable_1).zip_broadcast(iterable_2, scalar).into(list)
        [(1, 'a', '_'), (2, 'b', '_'), (3, 'c', '_')]

        If the strict keyword argument is True, then UnequalIterablesError will be raised if any of the iterables have different lengths.
        """

        return self.apply(lambda x: mit.zip_broadcast(x, *others, strict=strict))

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
    def zip_equal(self, *others: Iterable[Any]) -> Iter[tuple[Any, ...]]:
        """

        ``zip`` the input *iterables* together but raise ``UnequalIterablesError`` if they aren't all the same length.

        >>> import pychain as pc
        >>> pc.Iter.from_range(0, 3).zip_equal("abc").into(list)
        [(0, 'a'), (1, 'b'), (2, 'c')]
        >>> pc.Iter.from_range(0, 3).zip_equal("abcd").into(list)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        more_itertools.more.UnequalIterablesError: Iterables have different
        lengths

        """
        return self.apply(lambda x: mit.zip_equal(x, *others))

    def enumerate(self) -> Iter[tuple[int, T]]:
        """
        Return a Iter of (index, value) pairs.

        >>> import pychain as pc
        >>> pc.Iter(["a", "b"]).enumerate().into(list)
        [(0, 'a'), (1, 'b')]
        """
        return self.apply(enumerate)

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

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).combinations(2).into(list)
        [(1, 2), (1, 3), (2, 3)]
        """
        return self.apply(itertools.combinations, r)

    def zip_longest[U](
        self, *others: Iterable[T], fill_value: U = None
    ) -> Iter[tuple[U | T, ...]]:
        """
        Zip with other iterables, filling missing values.

        >>> import pychain as pc
        >>> pc.Iter([1, 2]).zip_longest([10], fill_value=0).into(list)
        [(1, 10), (2, 0)]
        """
        return self.apply(itertools.zip_longest, *others, fillvalue=fill_value)

    @overload
    def permutations(self, r: Literal[2]) -> Iter[tuple[T, T]]: ...
    @overload
    def permutations(self, r: Literal[3]) -> Iter[tuple[T, T, T]]: ...
    @overload
    def permutations(self, r: Literal[4]) -> Iter[tuple[T, T, T, T]]: ...
    @overload
    def permutations(self, r: Literal[5]) -> Iter[tuple[T, T, T, T, T]]: ...
    def permutations(self, r: int | None = None) -> Iter[tuple[T, ...]]:
        """
        Return all permutations of length r.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).permutations(2).into(list)
        [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
        """
        return self.apply(itertools.permutations, r)

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
    def product(self, *others: Iterable[Any]) -> Iter[tuple[Any, ...]]:
        """
        Computes the Cartesian product with another iterable.
        This is the declarative equivalent of nested for-loops.

        It pairs every element from the source iterable with every element from the
        other iterable.

        **Tip**: This method is often chained with `.starmap()` to apply a
        function to each generated pair.

        >>> import pychain as pc
        >>> colors = pc.Iter(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.product(sizes).into(list)
        [('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
        """
        return self.apply(itertools.product, *others)

    @overload
    def combinations_with_replacement(self, r: Literal[2]) -> Iter[tuple[T, T]]: ...
    @overload
    def combinations_with_replacement(self, r: Literal[3]) -> Iter[tuple[T, T, T]]: ...
    @overload
    def combinations_with_replacement(
        self, r: Literal[4]
    ) -> Iter[tuple[T, T, T, T]]: ...
    @overload
    def combinations_with_replacement(
        self, r: Literal[5]
    ) -> Iter[tuple[T, T, T, T, T]]: ...
    def combinations_with_replacement(self, r: int) -> Iter[tuple[T, ...]]:
        """
        Return all combinations with replacement of length r.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).combinations_with_replacement(2).into(list)
        [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
        """
        return self.apply(itertools.combinations_with_replacement, r)

    def pairwise(self) -> Iter[tuple[T, T]]:
        """
        Return an iterator over pairs of consecutive elements.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).pairwise().into(list)
        [(1, 2), (2, 3)]
        """
        return self.apply(itertools.pairwise)

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

        >>> import pychain as pc
        >>> colors = pc.Iter(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).into(list)
        [(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
        """

        return self.apply(
            lambda x: cz.itertoolz.join(
                leftkey=left_on,
                leftseq=x,
                rightkey=right_on,
                rightseq=other,
                left_default=left_default,
                right_default=right_default,
            )
        )

    def diff(
        self,
        *others: Iterable[T],
        default: T | None = None,
        key: Callable[[T], Any] | None = None,
    ) -> Iter[tuple[T, ...]]:
        """
        Return those items that differ between iterables.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).diff([1, 2, 10, 100], default=None).into(list)
        [(3, 10), (None, 100)]


        A key function may also be applied to each item to use during comparisons:

        >>> import pychain as pc
        >>> pc.Iter(["apples", "bananas"]).diff(
        ...     ["Apples", "Oranges"], key=str.lower
        ... ).into(list)
        [('bananas', 'Oranges')]
        """
        return self.apply(cz.itertoolz.diff, *others, default=default, key=key)

    @overload
    def map_juxt[R1, R2](
        self,
        func1: Callable[[T], R1],
        func2: Callable[[T], R2],
        /,
    ) -> Iter[tuple[R1, R2]]: ...
    @overload
    def map_juxt[R1, R2, R3](
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

        >>> import pychain as pc
        >>> pc.Iter([1, -2, 3]).map_juxt(lambda n: n % 2 == 0, lambda n: n > 0).into(
        ...     list
        ... )
        [(False, True), (True, False), (False, True)]
        """
        return self.apply(partial(map, cz.functoolz.juxt(*funcs)))
