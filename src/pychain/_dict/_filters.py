from collections.abc import Callable
from typing import Self

import cytoolz as cz

from .._core import CommonBase


class DictFilters[K, V](CommonBase[dict[K, V]]):
    def filter_keys(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_keys_not(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys_not(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """
        return self._new(cz.dicttoolz.keyfilter(lambda k: not predicate(k), self._data))

    def filter_values(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """
        return self._new(cz.dicttoolz.valfilter(predicate, self._data))

    def filter_values_not(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values_not(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """
        return self._new(cz.dicttoolz.valfilter(lambda v: not predicate(v), self._data))

    def filter_items(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items(lambda it: it[1] > 2).unwrap()
        {3: 4}
        """
        return self._new(cz.dicttoolz.itemfilter(predicate, self._data))

    def filter_items_not(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items_not(lambda it: it[1] > 2).unwrap()
        {1: 2}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: not predicate(kv), self._data)
        )

    def filter_kv(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2).unwrap()
        {3: 4}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: predicate(kv[0], kv[1]), self._data)
        )

    def filter_kv_not(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv_not(lambda k, v: v > 2).unwrap()
        {1: 2}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: not predicate(kv[0], kv[1]), self._data)
        )
