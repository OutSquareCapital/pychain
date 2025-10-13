from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import IterWrapper

if TYPE_CHECKING:
    from .._dict import Dict


class IterDicts[T](IterWrapper[T]):
    def group_by[K](self, on: Callable[[T], K]) -> Dict[K, list[T]]:
        """
        Group elements by key function and return a Dict result.

        >>> from pychain import Iter

        >>> names = [
        ...     "Alice",
        ...     "Bob",
        ...     "Charlie",
        ...     "Dan",
        ...     "Edith",
        ...     "Frank",
        ... ]
        >>> Iter(names).group_by(len).sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
            3, list: ['Bob', 'Dan'],
            5, list: ['Alice', 'Edith', 'Frank'],
            7, list: ['Charlie'],
        )
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
            False, list: [1, 3, 5, 7],
            True, list: [2, 4, 6, 8],
        )

        Non-callable keys imply grouping on a member.

        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
            'F', list: [{'name': 'Alice', 'gender': 'F'}],
            'M', list: [{'name': 'Bob', 'gender': 'M'}, {'name': 'Charlie', 'gender': 'M'}],
        )
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.groupby, on)))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.

        >>> from pychain import Iter
        >>> Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies().unwrap()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        from .._dict import Dict

        return Dict(self.into(cz.itertoolz.frequencies))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function

        >>> from pychain import Iter
        >>> Iter(["cat", "mouse", "dog"]).count_by(len).unwrap()
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> Iter([1, 2, 3]).count_by(iseven).unwrap()
        {False: 2, True: 1}
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.recipes.countby, key)))

    def with_keys[K](self, keys: Iterable[K]) -> Dict[K, T]:
        """
        Create a Dict by zipping the iterable with keys.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_keys(["a", "b", "c"]).unwrap()
        {'a': 1, 'b': 2, 'c': 3}
        """
        from .._dict import Dict

        return Dict(dict(zip(keys, self.unwrap())))

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_values(["a", "b", "c"]).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}
        """
        from .._dict import Dict

        return Dict(dict(zip(self.unwrap(), values)))
