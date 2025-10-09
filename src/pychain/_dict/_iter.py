from __future__ import annotations

from typing import TYPE_CHECKING

from .._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from .._iter import Iter


class IterDict[K, V](CommonBase[dict[K, V]]):
    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        return iter_factory(self._data.keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_values().into(list)
        [2]
        """
        return iter_factory(self._data.values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        return iter_factory(self._data.items())
