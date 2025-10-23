from __future__ import annotations

import itertools
from collections.abc import Callable, Generator, Iterable, Iterator
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

        Args:
            *others: Other iterables to zip with.
            strict: Whether to enforce equal lengths of iterables. Defaults to False.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2]).zip([10, 20]).into(list)
        [(1, 10), (2, 20)]
        >>> pc.Iter.from_(["a", "b"]).zip([1, 2, 3]).into(list)
        [('a', 1), ('b', 2)]

        ```
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

        Args:
            *others: Other iterables to zip with.
            offsets: List of integers specifying the offsets for each iterable.
            longest: Whether to continue until the longest iterable is exhausted. Defaults to False.
            fillvalue: Value to use for missing elements. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> data = pc.Seq("0123")
        >>> data.iter().zip_offset("abcdef", offsets=(0, 1)).into(list)
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e')]

        ```
        This can be used as a lightweight alternative to SciPy or pandas to analyze data sets in which some series have a lead or lag relationship.

        By default, the sequence will end when the shortest iterable is exhausted.

        To continue until the longest iterable is exhausted, set longest to True.
        ```python
        >>> data.iter().zip_offset("abcdef", offsets=(0, 1), longest=True).into(list)
        [('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e'), (None, 'f')]

        ```
        """

        def _zip_offset(data: Iterable[T]) -> Iterator[tuple[T | U, ...]]:
            return mit.zip_offset(
                data,
                *others,
                offsets=offsets,
                longest=longest,
                fillvalue=fillvalue,
            )

        return self.apply(_zip_offset)

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

        `str` and `bytes` are not treated as iterables.

        If the strict keyword argument is True, then UnequalIterablesError will be raised if any of the iterables have different lengths.
        Args:
            *others: Other iterables or scalars to zip with.
            strict: Whether to enforce equal lengths of iterables. Defaults to False.
        Example:
        ```python
        >>> import pyochain as pc
        >>> data = pc.Iter.from_([1, 2, 3])
        >>> other = ["a", "b", "c"]
        >>> scalar = "_"
        >>> data.zip_broadcast(other, scalar).into(list)
        [(1, 'a', '_'), (2, 'b', '_'), (3, 'c', '_')]

        ```
        """

        def _zip_broadcast(
            *objects: Iterable[Any],
        ) -> Generator[tuple[Iterable[Any], ...] | tuple[object, ...], Any, None]:
            """from more_itertools.zip_broadcast"""

            def is_scalar(obj: Any) -> bool:
                if isinstance(obj, (str, bytes)):
                    return True
                try:
                    iter(obj)
                except TypeError:
                    return True
                else:
                    return False

            size = len(objects)
            if not size:
                return

            new_item: list[object] = [None] * size
            iterables: list[Iterator[Any]] = []
            iterable_positions: list[int] = []
            for i, obj in enumerate(objects):
                if is_scalar(obj):
                    new_item[i] = obj
                else:
                    iterables.append(iter(obj))
                    iterable_positions.append(i)

            if not iterables:
                yield tuple(objects)
                return

            zipper = mit.zip_equal if strict else zip
            for item in zipper(*iterables):
                for i, new_item[i] in zip(iterable_positions, item):
                    pass
                yield tuple(new_item)

        return self.apply(_zip_broadcast, *others)

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
        `zip` the input *iterables* together but raise `UnequalIterablesError` if they aren't all the same length.

        Args:
            *others: Other iterables to zip with.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(range(3)).zip_equal("abc").into(list)
        [(0, 'a'), (1, 'b'), (2, 'c')]
        >>> pc.Iter.from_(range(3)).zip_equal("abcd").into(list)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        more_itertools.more.UnequalIterablesError: Iterables have different
        lengths

        ```
        """

        def _zip_equal(data: Iterable[T]) -> Iterator[tuple[Any, ...]]:
            return mit.zip_equal(data, *others)

        return self.apply(_zip_equal)

    def zip_longest[U](
        self, *others: Iterable[T], fill_value: U = None
    ) -> Iter[tuple[U | T, ...]]:
        """
        Zip with other iterables, filling missing values.

        Args:
            *others: Other iterables to zip with.
            fill_value: Value to use for missing elements. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2]).zip_longest([10], fill_value=0).into(list)
        [(1, 10), (2, 0)]

        ```
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

        Args:
            *others: Other iterables to compute the Cartesian product with.
        Example:
        ```python
        >>> import pyochain as pc
        >>> colors = pc.Iter.from_(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.product(sizes).into(list)
        [('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]

        ```
        """
        return self.apply(itertools.product, *others)

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
        Args:
            *others: Other iterables to compare with.
            default: Value to use for missing elements. Defaults to None.
            key: Function to apply to each item for comparison. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> data = pc.Seq([1, 2, 3])
        >>> data.iter().diff_at([1, 2, 10, 100], default=None).into(list)
        [(3, 10), (None, 100)]
        >>> data.iter().diff_at([1, 2, 10, 100, 2, 6, 7], default=0).into(list)
        [(3, 10), (0, 100), (0, 2), (0, 6), (0, 7)]

        A key function may also be applied to each item to use during comparisons:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(["apples", "bananas"]).diff_at(
        ...     ["Apples", "Oranges"], key=str.lower
        ... ).into(list)
        [('bananas', 'Oranges')]

        ```
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

        Args:
            other: Iterable to join with.
            left_on: Function to extract the join key from the left iterable.
            right_on: Function to extract the join key from the right iterable.
            left_default: Default value for missing elements in the left iterable. Defaults to None.
            right_default: Default value for missing elements in the right iterable. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> colors = pc.Iter.from_(["blue", "red"])
        >>> sizes = ["S", "M"]
        >>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).into(list)
        [(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]

        ```
        """

        def _join(data: Iterable[T]) -> Iterator[tuple[T, R]]:
            return cz.itertoolz.join(
                leftkey=left_on,
                leftseq=data,
                rightkey=right_on,
                rightseq=other,
                left_default=left_default,
                right_default=right_default,
            )

        return self.apply(_join)
