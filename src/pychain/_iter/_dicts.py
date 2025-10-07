from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import CommonBase, dict_factory

if TYPE_CHECKING:
    from .._dict import Dict


class IterDicts[T](CommonBase[Iterable[T]]):
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
        {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

        Non-callable keys imply grouping on a member.

        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        {'F': [{'name': 'Alice', 'gender': 'F'}], 'M': [{'name': 'Bob', 'gender': 'M'}, {'name': 'Charlie', 'gender': 'M'}]}
        """
        return dict_factory(cz.itertoolz.groupby(on, self._data))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.

        >>> from pychain import Iter
        >>> Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        return dict_factory(cz.itertoolz.frequencies(self._data))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function

        >>> from pychain import Iter
        >>> Iter(["cat", "mouse", "dog"]).count_by(len)
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> Iter([1, 2, 3]).count_by(iseven)
        {False: 2, True: 1}
        """
        return dict_factory(cz.recipes.countby(key, self._data))
