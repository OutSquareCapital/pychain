from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate

from .._core import MappingWrapper

if TYPE_CHECKING:
    from .._iter import Iter
    from ._main import Dict


class IterDict[K, V](MappingWrapper[K, V]):
    def itr[**P, R, U](
        self: Dict[K, Iterable[U]],  # type: ignore[misc]
        func: Callable[Concatenate[Iter[U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[K, R]:
        """
        Apply a function to each value after wrapping it in an Iter.
        Syntactic sugar for map_values(lambda data: func(Iter(data), *args, **kwargs))
        >>> import pychain as pc
        >>> data = {
        ...     "numbers1": [1, 2, 3],
        ...     "numbers2": [4, 5, 6],
        ... }
        >>> pc.Dict(data).itr(lambda v: v.repeat(5).explode().sum()).unwrap()
        {'numbers1': 30, 'numbers2': 75}
        """
        from .._iter import Iter

        return self.map_values(lambda data: func(Iter(data), *args, **kwargs))

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        from .._iter import Iter

        return Iter(self.unwrap().keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_values().into(list)
        [2]
        """
        from .._iter import Iter

        return Iter(self.unwrap().values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        from .._iter import Iter

        return Iter(self.unwrap().items())
