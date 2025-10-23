from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any

import cytoolz as cz

from .._core import IterWrapper, SupportsRichComparison

if TYPE_CHECKING:
    from ._main import Seq


class BaseEager[T](IterWrapper[T]):
    def sort[U: SupportsRichComparison[Any]](
        self: BaseEager[U], reverse: bool = False, key: Callable[[U], Any] | None = None
    ) -> Seq[U]:
        """
        Sort the elements of the sequence.

        Note:
            This method must consume the entire iterable to perform the sort.
            The result is a new iterable over the sorted sequence.

        Args:
            reverse: Whether to sort in descending order. Defaults to False.
            key: Function to extract a comparison key from each element. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([3, 1, 2]).sort().into(list)
        [1, 2, 3]

        ```
        """

        def _sort(data: Iterable[U]) -> list[U]:
            return sorted(data, reverse=reverse, key=key)

        return self.collect(_sort)

    def tail(self, n: int) -> Seq[T]:
        """
        Return a tuple of the last n elements.

        Args:
            n: Number of elements to return.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 3]).tail(2).unwrap()
        (2, 3)

        ```
        """
        return self.collect(partial(cz.itertoolz.tail, n))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Seq[T]:
        """
        Return a tuple of the top-n items according to key.

        Args:
            n: Number of top elements to return.
            key: Function to extract a comparison key from each element. Defaults to None.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 3, 2]).top_n(2).unwrap()
        (3, 2)

        ```
        """
        return self.collect(partial(cz.itertoolz.topk, n, key=key))

    def union(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the union of this iterable and 'others'.

        Note:
            This method consumes inner data and removes duplicates.

        Args:
            *others: Other iterables to include in the union.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 2]).union([2, 3], [4]).iter().sort().unwrap()
        [1, 2, 3, 4]

        ```
        """

        def _union(data: Iterable[T]) -> set[T]:
            return set(data).union(*others)

        return self.collect(_union)

    def intersection(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the elements common to this iterable and 'others'.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        Args:
            *others: Other iterables to intersect with.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 2]).intersection([2, 3], [2]).unwrap()
        {2}

        ```
        """

        def _intersection(data: Iterable[T]) -> set[T]:
            return set(data).intersection(*others)

        return self.collect(_intersection)

    def diff_unique(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the difference of this iterable and 'others'.
        (Elements in 'self' but not in 'others').

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        Args:
            *others: Other iterables to subtract from this iterable.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 2]).diff_unique([2, 3]).unwrap()
        {1}

        ```
        """

        def _difference(data: Iterable[T]) -> set[T]:
            return set(data).difference(*others)

        return self.collect(_difference)

    def diff_symmetric(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the symmetric difference (XOR) of this iterable and 'others'.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        Args:
            *others: Other iterables to compute the symmetric difference with.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 2]).diff_symmetric([2, 3]).iter().sort().unwrap()
        [1, 3]
        >>> pc.Iter.from_([1, 2, 3]).diff_symmetric([3, 4, 5]).iter().sort().unwrap()
        [1, 2, 4, 5]

        ```
        """

        def _symmetric_difference(data: Iterable[T]) -> set[T]:
            return set(data).symmetric_difference(*others)

        return self.collect(_symmetric_difference)

    def most_common(self, n: int | None = None) -> Seq[tuple[T, int]]:
        """
        Return the n most common elements and their counts.

        If n is None, then all elements are returned.

        Args:
            n: Number of most common elements to return. Defaults to None (all elements).

        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 1, 2, 3, 3, 3]).most_common(2).unwrap()
        [(3, 3), (1, 2)]

        ```
        """
        from collections import Counter

        from ._main import Seq

        def _most_common(data: Iterable[T]) -> list[tuple[T, int]]:
            return Counter(data).most_common(n)

        return Seq(self.into(_most_common))
