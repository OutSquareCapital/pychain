from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate

import cytoolz as cz

from .._core import MappingWrapper

if TYPE_CHECKING:
    from .._iter import Iter
    from ._main import Dict


class IterDict[K, V](MappingWrapper[K, V]):
    def itr[**P, R, U](
        self: MappingWrapper[K, Iterable[U]],
        func: Callable[Concatenate[Iter[U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[K, R]:
        """
        Apply a function to each value after wrapping it in an Iter.

        Syntactic sugar for ``map_values(lambda data: func(Iter(data), *args, **kwargs))``
        >>> import pychain as pc
        >>> data = {
        ...     "numbers1": [1, 2, 3],
        ...     "numbers2": [4, 5, 6],
        ... }
        >>> pc.Dict(data).itr(lambda v: v.repeat(5).explode().sum()).unwrap()
        {'numbers1': 30, 'numbers2': 75}
        """
        from .._iter import Iter

        return self.apply(
            lambda data: cz.dicttoolz.valmap(
                lambda v: func(Iter.from_(v), *args, **kwargs), data
            )
        )

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> import pychain as pc
        >>> pc.Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        from .._iter import Iter

        return Iter.from_(self.unwrap().keys())

    def iter_values(self) -> Iter[V]:
        """
        Return an Iter of the dict's values.

        >>> import pychain as pc
        >>> pc.Dict({1: 2}).iter_values().into(list)
        [2]
        """
        from .._iter import Iter

        return Iter.from_(self.unwrap().values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> import pychain as pc
        >>> pc.Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        from .._iter import Iter

        return Iter.from_(self.unwrap().items())
