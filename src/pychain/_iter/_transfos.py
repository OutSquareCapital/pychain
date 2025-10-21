from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING

import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class BaseTransfos[T](IterWrapper[T]):
    def adjacent(
        self, predicate: Callable[[T], bool], distance: int = 1
    ) -> Iter[tuple[bool, T]]:
        """
        Return an iterable over (bool, item) tuples.

        The output is a sequence of tuples where the item is drawn from iterable.

        The bool indicates whether that item satisfies the predicate or is adjacent to an item that does.

        For example, to find whether items are adjacent to a 3:
        >>> import pychain as pc
        >>> pc.Iter.from_range(0, 6).adjacent(lambda x: x == 3).into(list)
        [(False, 0), (False, 1), (True, 2), (True, 3), (True, 4), (False, 5)]

        Set distance to change what counts as adjacent. For example, to find whether items are two places away from a 3:
        >>> pc.Iter.from_range(0, 6).adjacent(lambda x: x == 3, distance=2).into(list)
        [(False, 0), (True, 1), (True, 2), (True, 3), (True, 4), (True, 5)]

        This is useful for contextualizing the results of a search function.

        For example, a code comparison tool might want to identify lines that have changed, but also surrounding lines to give the viewer of the diff context.

        The predicate function will only be called once for each item in the iterable.

        See also groupby_transform, which can be used with this function to group ranges of items with the same bool value.
        """
        return self.apply(partial(mit.adjacent, predicate, distance=distance))

    def most_common(self, n: int | None = None) -> Iter[tuple[T, int]]:
        """
        Return an iterable over the n most common elements and their counts from the most common to the least.

        If n is None, then all elements are returned.
        >>> import pychain as pc
        >>> pc.Iter([1, 1, 2, 3, 3, 3]).most_common(2).into(list)
        [(3, 3), (1, 2)]
        """
        from collections import Counter

        def _most_common(data: Iterable[T]) -> list[tuple[T, int]]:
            return Counter(data).most_common(n)

        return self.apply(_most_common)

    def classify_unique(self) -> Iter[tuple[T, bool, bool]]:
        """
        Classify each element in terms of its uniqueness.

        For each element in the input iterable, return a 3-tuple consisting of:
        - The element itself
        - False if the element is equal to the one preceding it in the input, True otherwise (i.e. the equivalent of unique_justseen)
        - False if this element has been seen anywhere in the input before, True otherwise (i.e. the equivalent of unique_everseen)
        >>> import pychain as pc
        >>> pc.Iter("otto").classify_unique().into(
        ...     list
        ... )  # doctest: +NORMALIZE_WHITESPACE
        [('o', True,  True),
        ('t', True,  True),
        ('t', False, False),
        ('o', True,  False)]

        This function is analogous to unique_everseen and is subject to the same performance considerations.
        """
        return self.apply(mit.classify_unique)
