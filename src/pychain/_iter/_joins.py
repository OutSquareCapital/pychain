from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class BaseJoins[T](IterWrapper[T]):
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

    def union(self, *others: Iterable[T]) -> Iter[T]:
        """
        Return the union of this iterable and 'others' as a new Iter.

        Note:
            This method consumes inner data and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).union([2, 3], [4]).sort().into(list)
        [1, 2, 3, 4]
        """
        return self.apply(lambda data: set(data).union(*others))

    def intersection(self, *others: Iterable[T]) -> Iter[T]:
        """
        Return the elements common of this iterable and 'others'.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.


        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).intersection([2, 3], [2]).into(list)
        [2]
        """
        return self.apply(lambda data: set(data).intersection(*others))

    def diff_unique(self, *others: Iterable[T]) -> Iter[T]:
        """
        Return the difference of this iterable and 'others' as a new Iter.

        (Elements in 'self' but not in 'others').

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).diff_unique([2, 3]).into(list)
        [1]
        """
        return self.apply(lambda data: set(data).difference(*others))

    def diff_symmetric(self, *others: Iterable[T]) -> Iter[T]:
        """
        Return the symmetric difference (XOR) of this iterable and 'other'
        as a new Iter.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).diff_symmetric([2, 3]).sort().into(list)
        [1, 3]
        >>> pc.Iter([1, 2, 3]).diff_symmetric([3, 4, 5]).sort().into(list)
        [1, 2, 4, 5]
        """
        return self.apply(lambda data: set(data).symmetric_difference(*others))

    def diff_at(
        self,
        *others: Iterable[T],
        default: T | None = None,
        key: Callable[[T], Any] | None = None,
    ) -> Iter[tuple[T, ...]]:
        """
        Return those items that differ between iterables.

        Each output item is a tuple where the i-th element is from the i-th input iterable.
        If an input iterable is exhausted before others, then the corresponding output items will be filled with *default*.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).diff_at([1, 2, 10, 100], default=None).into(list)
        [(3, 10), (None, 100)]
        >>> pc.Iter([1, 2, 3]).diff_at([1, 2, 10, 100, 2, 6, 7], default=0).into(list)
        [(3, 10), (0, 100), (0, 2), (0, 6), (0, 7)]


        A key function may also be applied to each item to use during comparisons:

        >>> import pychain as pc
        >>> pc.Iter(["apples", "bananas"]).diff_at(
        ...     ["Apples", "Oranges"], key=str.lower
        ... ).into(list)
        [('bananas', 'Oranges')]
        """
        return self.apply(cz.itertoolz.diff, *others, default=default, key=key)

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
