from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import IterWrapper

if TYPE_CHECKING:
    from .._dict import Dict


class BaseGroups[T](IterWrapper[T]):
    def reduce_by[K](
        self, key: Callable[[T], K], binop: Callable[[T, T], T]
    ) -> Dict[K, T]:
        """
        Perform a simultaneous groupby and reduction
        >>> from collections.abc import Iterable
        >>> import pychain as pc
        >>> from operator import add, mul
        >>>
        >>> def is_even(x: int) -> bool:
        ...     return x % 2 == 0
        >>>
        >>> def group_reduce(data: Iterable[int]) -> int:
        ...     return pc.Iter(data).reduce(add)
        >>>
        >>> data = pc.Iter([1, 2, 3, 4, 5])
        >>> data.reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> data.group_by(is_even).map_values(group_reduce).unwrap()
        {False: 9, True: 6}

        But the former does not build the intermediate groups, allowing it to operate in much less space.

        This makes it suitable for larger datasets that do not fit comfortably in memory

        Simple Examples
        >>> pc.Iter([1, 2, 3, 4, 5]).reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> pc.Iter([1, 2, 3, 4, 5]).reduce_by(is_even, mul).unwrap()
        {False: 15, True: 8}
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.reduceby, key, binop)))

    def group_by[K](self, on: Callable[[T], K]) -> Dict[K, list[T]]:
        """
        Group elements by key function and return a Dict result.
        >>> import pychain as pc
        >>> names = [
        ...     "Alice",
        ...     "Bob",
        ...     "Charlie",
        ...     "Dan",
        ...     "Edith",
        ...     "Frank",
        ... ]
        >>> pc.Iter(names).group_by(len).sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            3: ['Bob', 'Dan'],
            5: ['Alice', 'Edith', 'Frank'],
            7: ['Charlie']
        })
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> pc.Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            False: [1, 3, 5, 7],
            True: [2, 4, 6, 8]
        })

        Non-callable keys imply grouping on a member.
        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> pc.Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            'F': [
                {'name': 'Alice', 'gender': 'F'}
            ],
            'M': [
                {'name': 'Bob', 'gender': 'M'},
                {'name': 'Charlie', 'gender': 'M'}
            ]
        })
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.groupby, on)))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.
        >>> import pychain as pc
        >>> pc.Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies().unwrap()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        from .._dict import Dict

        return Dict(self.into(cz.itertoolz.frequencies))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function
        >>> import pychain as pc
        >>> pc.Iter(["cat", "mouse", "dog"]).count_by(len).unwrap()
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> pc.Iter([1, 2, 3]).count_by(iseven).unwrap()
        {False: 2, True: 1}
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.recipes.countby, key)))
