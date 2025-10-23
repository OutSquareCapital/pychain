from __future__ import annotations

import itertools
from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING, Literal, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class BaseTuples[T](IterWrapper[T]):
    def enumerate(self) -> Iter[tuple[int, T]]:
        """
        Return a Iter of (index, value) pairs.
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(["a", "b"]).enumerate().into(list)
        [(0, 'a'), (1, 'b')]

        ```
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

        Args:
            r: Length of each combination.

        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 3]).combinations(2).into(list)
        [(1, 2), (1, 3), (2, 3)]

        ```
        """
        return self.apply(itertools.combinations, r)

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

        Args:
            r: Length of each permutation. Defaults to the length of the iterable.

        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 3]).permutations(2).into(list)
        [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

        ```
        """
        return self.apply(itertools.permutations, r)

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

        Args:
            r: Length of each combination.

        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 3]).combinations_with_replacement(2).into(list)
        [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]

        ```
        """
        return self.apply(itertools.combinations_with_replacement, r)

    def pairwise(self) -> Iter[tuple[T, T]]:
        """
        Return an iterator over pairs of consecutive elements.
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_([1, 2, 3]).pairwise().into(list)
        [(1, 2), (2, 3)]

        ```
        """
        return self.apply(itertools.pairwise)

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
        ```python
        >>> import pyochain as pc
        >>> def is_even(n: int) -> bool:
        ...     return n % 2 == 0
        >>> def is_positive(n: int) -> bool:
        ...     return n > 0
        >>>
        >>> pc.Iter.from_([1, -2, 3]).map_juxt(is_even, is_positive).into(list)
        [(False, True), (True, False), (False, True)]

        ```
        """
        return self.apply(partial(map, cz.functoolz.juxt(*funcs)))

    def adjacent(
        self, predicate: Callable[[T], bool], distance: int = 1
    ) -> Iter[tuple[bool, T]]:
        """
        Return an iterable over (bool, item) tuples.

        Args:
            predicate: Function to determine if an item satisfies the condition.
            distance: Number of places to consider as adjacent. Defaults to 1.

        The output is a sequence of tuples where the item is drawn from iterable.

        The bool indicates whether that item satisfies the predicate or is adjacent to an item that does.

        For example, to find whether items are adjacent to a 3:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(range(6)).adjacent(lambda x: x == 3).into(list)
        [(False, 0), (False, 1), (True, 2), (True, 3), (True, 4), (False, 5)]

        ```
        Set distance to change what counts as adjacent.
        For example, to find whether items are two places away from a 3:
        ```python
        >>> pc.Iter.from_(range(6)).adjacent(lambda x: x == 3, distance=2).into(list)
        [(False, 0), (True, 1), (True, 2), (True, 3), (True, 4), (True, 5)]

        ```

        This is useful for contextualizing the results of a search function.

        For example, a code comparison tool might want to identify lines that have changed, but also surrounding lines to give the viewer of the diff context.

        The predicate function will only be called once for each item in the iterable.

        See also groupby_transform, which can be used with this function to group ranges of items with the same bool value.
        """
        return self.apply(partial(mit.adjacent, predicate, distance=distance))

    def classify_unique(self) -> Iter[tuple[T, bool, bool]]:
        """
        Classify each element in terms of its uniqueness.\n
        For each element in the input iterable, return a 3-tuple consisting of:

        - The element itself
        - False if the element is equal to the one preceding it in the input, True otherwise (i.e. the equivalent of unique_justseen)
        - False if this element has been seen anywhere in the input before, True otherwise (i.e. the equivalent of unique_everseen)
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_("otto").classify_unique().into(list)
        ... # doctest: +NORMALIZE_WHITESPACE
        [('o', True,  True),
        ('t', True,  True),
        ('t', False, False),
        ('o', True,  False)]

        ```

        This function is analogous to unique_everseen and is subject to the same performance considerations.
        """
        return self.apply(mit.classify_unique)
