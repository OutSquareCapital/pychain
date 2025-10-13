from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Concatenate

from . import funcs as fn
from ._constructors import DictConstructors
from ._core import CoreDict
from ._filters import DictFilters


class Dict[K, V](CoreDict[K, V], DictFilters[K, V], DictConstructors):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    __slots__ = ("_data",)

    def pipe_into[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[K, V], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[KU, VU]:
        """
        Apply a function to the underlying dict and return a new Dict.

        >>> from pychain import Dict
        >>>
        >>> def mul_by_ten(d: dict[int, int]) -> dict[int, int]:
        ...     return {k: v * 10 for k, v in d.items()}
        >>>
        >>> Dict({1: 20, 2: 30}).pipe_into(mul_by_ten).unwrap()
        {1: 200, 2: 300}
        """
        return super().pipe_into(func, *args, **kwargs)

    def implode(self) -> Dict[K, Iterable[V]]:
        """
        Nest all the values in lists.
        syntactic sugar for map_values(lambda v: [v])

        >>> Dict({1: 2, 3: 4}).implode().unwrap()
        {1: [2], 3: [4]}
        """
        return self.map_values(lambda v: [v])

    def map_keys[T](self, func: Callable[[K], T]) -> Dict[T, V]:
        """
        Return a Dict with keys transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(str.lower).unwrap()
        {'alice': [20, 15, 30], 'bob': [10, 35]}
        >>>
        >>> Dict({1: "a"}).map_keys(str).unwrap()
        {'1': 'a'}
        """
        return self.pipe_into(fn.map_keys, func)

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}
        """
        return self.pipe_into(fn.map_values, func)

    def map_items[KR, VR](
        self,
        func: Callable[[tuple[K, V]], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes a (key, value) tuple.

        >>> Dict({"Alice": 10, "Bob": 20}).map_items(
        ...     lambda kv: (kv[0].upper(), kv[1] * 2)
        ... ).unwrap()
        {'ALICE': 20, 'BOB': 40}
        """
        return self.pipe_into(fn.map_items, func)

    def reverse(self) -> Dict[V, K]:
        """
        Return a new Dict with keys and values swapped.

        Values in the original dict must be unique and hashable.

        >>> Dict({"a": 1, "b": 2}).reverse().unwrap()
        {1: 'a', 2: 'b'}
        """
        return self.pipe_into(fn.reverse)

    def flip(self) -> Dict[V, list[K]]:
        """
        Return a new Dict with keys and values swapped, grouping original keys in a list if values are not unique.

        Values in the original dict must be hashable.

        >>> Dict({"a": 1, "b": 2, "c": 1}).flip().unwrap()
        {1: ['a', 'c'], 2: ['b']}
        """
        return self.pipe_into(fn.flip_item)

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}
        """
        return self.pipe_into(fn.map_kv, func)

    def diff(self, other: dict[K, V]) -> Dict[K, tuple[V | None, V | None]]:
        """
        Returns a dict of the differences between this dict and another.

        The keys of the returned dict are the keys that are not shared or have different values.
        The values are tuples containing the value from self and the value from other.

        >>> d1 = {"a": 1, "b": 2, "c": 3}
        >>> d2 = {"b": 2, "c": 4, "d": 5}
        >>> Dict(d1).diff(d2).sort().unwrap()
        {'a': (1, None), 'c': (3, 4), 'd': (None, 5)}
        """
        return self.pipe_into(fn.diff, other)

    def join_mappings(
        self,
        main_name: str = "main",
        **field_to_map: dict[K, V],
    ) -> Dict[K, dict[str, V]]:
        """
        Join multiple mappings into a single mapping of mappings.
        Each key in the resulting dict maps to a dict containing values from the original dict and the additional mappings, keyed by their respective names.
        >>> Dict({"a": 1, "b": 2}).join_mappings(
        ...     main_name="score", time={"a": 10, "b": 20}
        ... ).unwrap()
        {'a': {'score': 1, 'time': 10}, 'b': {'score': 2, 'time': 20}}
        """
        return self.pipe_into(fn.join_mapping, main_name, **field_to_map)
