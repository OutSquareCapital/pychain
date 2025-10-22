from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper, SupportsRichComparison

if TYPE_CHECKING:
    from ._main import Seq


class BaseEager[T](IterWrapper[T]):
    def sort[U: SupportsRichComparison[Any]](
        self: BaseEager[U], reverse: bool = False, key: Callable[[U], Any] | None = None
    ) -> Seq[U]:
        """
        Sort the elements of the sequence.
        Note: This method must consume the entire iterable to perform the sort.

        The result is a new iterable over the sorted sequence.

        >>> import pychain as pc
        >>> pc.Iter([3, 1, 2]).sort().into(list)
        [1, 2, 3]
        """

        def _sort(data: Iterable[U]) -> list[U]:
            return sorted(data, reverse=reverse, key=key)

        return self.collect(_sort)

    def tail(self, n: int) -> Seq[T]:
        """
        Return last n elements wrapped.
        >>> import pychain as pc
        >>> pc.Iter([1, 2, 3]).tail(2).unwrap()
        [2, 3]
        """
        return self.collect(partial(cz.itertoolz.tail, n))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Seq[T]:
        """
        Return a tuple of the top-n items according to key.
        >>> import pychain as pc
        >>> pc.Iter([1, 3, 2]).top_n(2).unwrap()
        (3, 2)
        """
        return self.collect(partial(cz.itertoolz.topk, n, key=key))

    def union(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the union of this iterable and 'others' as a new Iter.

        Note:
            This method consumes inner data and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).union([2, 3], [4]).iter().sort().into(list)
        [1, 2, 3, 4]
        """

        def _union(data: Iterable[T]) -> set[T]:
            return set(data).union(*others)

        return self.collect(_union)

    def intersection(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the elements common of this iterable and 'others'.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).intersection([2, 3], [2]).into(list)
        [2]
        """

        def _intersection(data: Iterable[T]) -> set[T]:
            return set(data).intersection(*others)

        return self.collect(_intersection)

    def diff_unique(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the difference of this iterable and 'others' as a new Iter.

        (Elements in 'self' but not in 'others').

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).diff_unique([2, 3]).into(list)
        [1]
        """

        def _difference(data: Iterable[T]) -> set[T]:
            return set(data).difference(*others)

        return self.collect(_difference)

    def diff_symmetric(self, *others: Iterable[T]) -> Seq[T]:
        """
        Return the symmetric difference (XOR) of this iterable and 'other'
        as a new Iter.

        Note:
            This method consumes inner data, unsorts it, and removes duplicates.

        >>> import pychain as pc
        >>> pc.Iter([1, 2, 2]).diff_symmetric([2, 3]).iter().sort().into(list)
        [1, 3]
        >>> pc.Iter([1, 2, 3]).diff_symmetric([3, 4, 5]).iter().sort().into(list)
        [1, 2, 4, 5]
        """

        def _symmetric_difference(data: Iterable[T]) -> set[T]:
            return set(data).symmetric_difference(*others)

        return self.collect(_symmetric_difference)

    def unique_to_each(self, *others: Iterable[T]) -> Seq[list[T]]:
        """
        Return the elements from each of the input iterables that aren't in the other input iterables.

        For example, suppose you have a set of packages, each with a set of dependencies:

        **{'pkg_1': {'A', 'B'}, 'pkg_2': {'B', 'C'}, 'pkg_3': {'B', 'D'}}**

        If you remove one package, which dependencies can also be removed?

        If pkg_1 is removed, then A is no longer necessary - it is not associated with pkg_2 or pkg_3.

        Similarly, C is only needed for pkg_2, and D is only needed for pkg_3:

        >>> import pychain as pc
        >>> pc.Iter({"A", "B"}).unique_to_each({"B", "C"}, {"B", "D"}).unwrap()
        [['A'], ['C'], ['D']]

        If there are duplicates in one input iterable that aren't in the others they will be duplicated in the output.

        Input order is preserved:
        >>> pc.Iter("mississippi").unique_to_each("missouri").unwrap()
        [['p', 'p'], ['o', 'u', 'r']]

        It is assumed that the elements of each iterable are hashable.
        """
        from ._main import Seq

        return Seq(self.into(mit.unique_to_each, *others))

    def most_common(self, n: int | None = None) -> Seq[tuple[T, int]]:
        """
        Return a Sequence over the n most common elements and their counts from the most common to the least.

        If n is None, then all elements are returned.
        >>> import pychain as pc
        >>> pc.Iter([1, 1, 2, 3, 3, 3]).most_common(2).into(list)
        [(3, 3), (1, 2)]
        """
        from collections import Counter

        from ._main import Seq

        def _most_common(data: Iterable[T]) -> list[tuple[T, int]]:
            return Counter(data).most_common(n)

        return Seq(self.into(_most_common))
