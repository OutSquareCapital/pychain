from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Concatenate

import cytoolz as cz
import more_itertools as mit

from ._constructors import DictConstructors
from ._core import CoreDict
from ._filters import DictFilters


class Dict[K, V](CoreDict[K, V], DictFilters[K, V], DictConstructors):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    _data: dict[K, V]
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
        return Dict(func(self._data, *args, **kwargs))

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
        return Dict(cz.dicttoolz.keymap(func, self._data))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}
        """
        return Dict(cz.dicttoolz.valmap(func, self._data))

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
        return Dict(cz.dicttoolz.itemmap(func, self._data))

    def reverse(self) -> Dict[V, K]:
        """
        Return a new Dict with keys and values swapped.

        Values in the original dict must be unique and hashable.

        >>> Dict({"a": 1, "b": 2}).reverse().unwrap()
        {1: 'a', 2: 'b'}
        """
        return Dict(cz.dicttoolz.itemmap(reversed, self._data))

    def flip(self) -> Dict[V, list[K]]:
        """
        Return a new Dict with keys and values swapped, grouping original keys in a list if values are not unique.

        Values in the original dict must be hashable.

        >>> Dict({"a": 1, "b": 2, "c": 1}).flip().unwrap()
        {1: ['a', 'c'], 2: ['b']}
        """
        flipped: dict[V, list[K]] = {}
        for key, value in self._data.items():
            if value in flipped:
                flipped[value].append(key)
            else:
                flipped[value] = [key]
        return Dict(flipped)

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), self._data))

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
        all_keys: set[K] = self._data.keys() | other.keys()
        diffs: dict[K, tuple[V | None, V | None]] = {}
        for key in all_keys:
            self_val = self._data.get(key)
            other_val = other.get(key)
            if self_val != other_val:
                diffs[key] = (self_val, other_val)
        return Dict(diffs)

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
        all_maps = {
            main_name: self.unwrap(),
            **{k: v for k, v in field_to_map.items()},
        }
        return Dict(mit.join_mappings(**all_maps))

    def flatten(
        self: Dict[str, Any], sep: str = ".", max_depth: int | None = None
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary, concatenating keys with the specified separator.

        Args:
            sep: Separator to use when concatenating keys
            max_depth: Maximum depth to flatten. If None, flattens completely.

        >>> import pychain as pc
        >>> data = {
        ...     "config": {"params": {"retries": 3, "timeout": 30}, "mode": "fast"},
        ...     "version": 1.0,
        ... }
        >>> pc.Dict(data).flatten().unwrap()
        {'config.params.retries': 3, 'config.params.timeout': 30, 'config.mode': 'fast', 'version': 1.0}
        >>> pc.Dict(data).flatten(sep="_").unwrap()
        {'config_params_retries': 3, 'config_params_timeout': 30, 'config_mode': 'fast', 'version': 1.0}
        >>> pc.Dict(data).flatten(max_depth=1).unwrap()
        {'config.params': {'retries': 3, 'timeout': 30}, 'config.mode': 'fast', 'version': 1.0}

        """

        def _recurse_flatten(
            d: dict[Any, Any], parent_key: str = "", current_depth: int = 1
        ) -> dict[str, Any]:
            items: list[tuple[str, Any]] = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, dict) and (
                    max_depth is None or current_depth < max_depth + 1
                ):
                    items.extend(
                        _recurse_flatten(v, new_key, current_depth + 1).items()  # type: ignore
                    )
                else:
                    items.append((new_key, v))  # type: ignore
            return dict(items)

        return self._new(_recurse_flatten(self._data))

    def schema(self, max_depth: int = 2) -> Dict[str, Any]:
        """
        Return the schema of the dictionary up to a maximum depth.
        When the max depth is reached, nested dicts are marked as 'dict'.
        For lists, only the first element is inspected.

        >>> import pychain as pc
        >>> # Depth 2: we see up to level2
        >>> data = {"level1": {"level2": {"level3": {"key": "value"}}}}
        >>> pc.Dict(data).schema().unwrap()
        {'level1': {'level2': 'dict'}}
        >>>
        >>> # Depth 3: we see up to level3
        >>> pc.Dict(data).schema(max_depth=3).unwrap()
        {'level1': {'level2': {'level3': 'dict'}}}
        """

        def get_structure(node: Any, current_depth: int) -> Any:
            if isinstance(node, dict):
                if current_depth >= max_depth:
                    return "dict"
                return {
                    k: get_structure(v, current_depth + 1)
                    for k, v in node.items()  # type: ignore
                }
            elif cz.itertoolz.isiterable(node):
                if current_depth >= max_depth:
                    return type(node).__name__
                return get_structure(cz.itertoolz.first(node), current_depth + 1)
            else:
                return type(node).__name__

        return Dict(get_structure(self._data, 0))
