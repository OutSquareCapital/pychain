from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import Concatenate

import cytoolz as cz

from ._core import CoreDict


class Dict[K, V](CoreDict[K, V]):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    def apply[**P, KU, VU](
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
        >>> Dict({1: 20, 2: 30}).apply(mul_by_ten).unwrap()
        {1: 200, 2: 300}
        """
        return super().apply(func, *args, **kwargs)

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
        return self.apply(partial(cz.dicttoolz.keymap, func))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}
        """
        return self.apply(partial(cz.dicttoolz.valmap, func))

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
        return self.apply(partial(cz.dicttoolz.itemmap, func))

    def reverse(self) -> Dict[V, K]:
        """
        Return a new Dict with keys and values swapped.

        Values in the original dict must be unique and hashable.

        >>> Dict({"a": 1, "b": 2}).reverse().unwrap()
        {1: 'a', 2: 'b'}
        """
        return self.apply(partial(cz.dicttoolz.itemmap, reversed))

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}
        """
        return self.apply(
            lambda data: cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), data)
        )

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

        def _(data: dict[K, V]) -> dict[K, tuple[V | None, V | None]]:
            all_keys: set[K] = data.keys() | other.keys()
            diffs: dict[K, tuple[V | None, V | None]] = {}
            for key in all_keys:
                self_val = data.get(key)
                other_val = other.get(key)
                if self_val != other_val:
                    diffs[key] = (self_val, other_val)
            return diffs

        return self.apply(_)
