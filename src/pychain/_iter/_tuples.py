from __future__ import annotations

import itertools
from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING, Literal, overload

import cytoolz as cz

from .._core import IterWrapper

if TYPE_CHECKING:
    from ._main import Iter


class BaseTuples[T](IterWrapper[T]):
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
