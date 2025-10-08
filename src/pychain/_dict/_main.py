from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self, overload

import cytoolz as cz
import more_itertools as mit

from .._core import iter_factory
from ._constructors import DictConstructors
from ._process import ProcessDict

if TYPE_CHECKING:
    from .._core import Iter


class Dict[K, V](ProcessDict[K, V], DictConstructors):
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
        return Dict(func(self._data, *args, **kwargs))

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

            >>> Dict({1: 2}).iter_keys().into(list)
            [1]
        """
        return iter_factory(self._data.keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

            >>> Dict({1: 2}).iter_values().into(list)
            [2]
        """
        return iter_factory(self._data.values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

            >>> Dict({1: 2}).iter_items().into(list)
            [(1, 2)]
        """
        return iter_factory(self._data.items())

    def implode(self) -> Dict[K, Iterable[V]]:
        """
        Nest all the values in lists.
        syntactic sugar for map_values(lambda v: [v]).

        >>> Dict({1: 2, 3: 4}).implode()
        {1: [2], 3: [4]}
        """
        return self.map_values(lambda v: [v])

    @overload
    def get_nested(self, *keys: K, default: V) -> V: ...
    @overload
    def get_nested[T](self, *keys: K, default: T) -> V | T: ...
    @overload
    def get_nested(self, *keys: K) -> V | None: ...

    def get_nested[T](self, *keys: K, default: T = None) -> V | T:
        """
        Get a value from a nested dictionary.

        Returns the value at the path specified by keys. If the path does not exist, returns the default value. This is a terminal operation.

        >>> purchase = {
        ...     "user": {"name": "Alice"},
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ... }
        >>> Dict(purchase).get_nested("order", "costs")
        [0.5, 1.25]
        >>> Dict(purchase).get_nested("user", "age", default=99)
        99
        """
        return cz.dicttoolz.get_in(keys, self._data, default)

    def update_in(
        self, *keys: K, func: Callable[[V], V], default: V | None = None
    ) -> Self:
        """
        Update value in a (potentially) nested dictionary.

        Applies the func to the value at the path specified by keys, returning a new Dict with the updated value.

        If the path does not exist, it will be created with the default value (if provided) before applying func.

        >>> inc = lambda x: x + 1
        >>> Dict({"a": 0}).update_in("a", func=inc)
        {'a': 1}
        >>> transaction = {
        ...     "name": "Alice",
        ...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> Dict(transaction).update_in("purchase", "costs", func=sum)
        {'name': 'Alice', 'purchase': {'items': ['Apple', 'Orange'], 'costs': 1.75}, 'credit card': '5555-1234-1234-1234'}
        >>> # updating a value when k0 is not in d
        >>> Dict({}).update_in(1, 2, 3, func=str, default="bar")
        {1: {2: {3: 'bar'}}}
        >>> Dict({1: "foo"}).update_in(2, 3, 4, func=inc, default=0)
        {1: 'foo', 2: {3: {4: 1}}}

        """
        return self._new(
            cz.dicttoolz.update_in(self._data, keys, func=func, default=default)
        )

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merge other dicts into this one and return a new Dict.

        >>> Dict({1: "one"}).merge({2: "two"})
        {1: 'one', 2: 'two'}

        Later dictionaries have precedence

        >>> Dict({1: 2, 3: 4}).merge({3: 3, 4: 4})
        {1: 2, 3: 3, 4: 4}
        """
        return self._new(cz.dicttoolz.merge(self._data, *others))

    def merge_with(self, *others: dict[K, V], func: Callable[[Iterable[V]], V]) -> Self:
        """
        Merge dicts using a function to combine values for duplicate keys.

        A key may occur in more than one dict, and all values mapped from the key will be passed to the function as a list, such as func([val1, val2, ...]).

        >>> Dict({1: 1, 2: 2}).merge_with({1: 10, 2: 20}, func=sum)
        {1: 11, 2: 22}
        >>> Dict({1: 1, 2: 2}).merge_with({2: 20, 3: 30}, func=max)
        {1: 1, 2: 20, 3: 30}

        """
        return self._new(cz.dicttoolz.merge_with(func, self._data, *others))

    def drop(self, *keys: K) -> Self:
        """
        Return a new Dict with given keys removed.

        New dict has d[key] deleted for each supplied key.

        >>> Dict({"x": 1, "y": 2}).drop("y")
        {'x': 1}
        >>> Dict({"x": 1, "y": 2}).drop("y", "x")
        {}
        >>> Dict({"x": 1}).drop("y")  # Ignores missing keys
        {'x': 1}
        >>> Dict({1: 2, 3: 4}).drop(1)
        {3: 4}
        """
        return self._new(cz.dicttoolz.dissoc(self._data, *keys))

    def map_keys[T](self, func: Callable[[K], T]) -> Dict[T, V]:
        """
        Return a Dict with keys transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(str.lower)
        {'alice': [20, 15, 30], 'bob': [10, 35]}
        >>>
        >>> Dict({1: "a"}).map_keys(str)
        {'1': 'a'}
        """
        return Dict(cz.dicttoolz.keymap(func, self._data))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum)
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> Dict({1: 1}).map_values(lambda v: v + 1)
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
        ... )
        {'ALICE': 20, 'BOB': 40}
        """
        return Dict(cz.dicttoolz.itemmap(func, self._data))

    def reverse(self) -> Dict[V, K]:
        """
        Return a new Dict with keys and values swapped.

        Values in the original dict must be unique and hashable.

        >>> Dict({"a": 1, "b": 2}).reverse()
        {1: 'a', 2: 'b'}
        """
        return Dict(cz.dicttoolz.itemmap(reversed, self._data))

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10))
        {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), self._data))

    def flip(self) -> Dict[V, list[K]]:
        """
        Return a new Dict with keys and values swapped, grouping original keys in a list if values are not unique.

        Values in the original dict must be hashable.

        >>> Dict({"a": 1, "b": 2, "c": 1}).flip()
        {1: ['a', 'c'], 2: ['b']}
        """
        flipped: dict[V, list[K]] = {}
        for key, value in self._data.items():
            if value in flipped:
                flipped[value].append(key)
            else:
                flipped[value] = [key]
        return Dict(flipped)

    def rename_keys(self, mapping: dict[K, K]) -> Dict[K, V]:
        """
        Return a new Dict with keys renamed according to the mapping.

        Keys not in the mapping are kept as is.

        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> mapping = {"b": "beta", "c": "gamma"}
        >>> Dict(d).rename_keys(mapping)
        {'a': 1, 'beta': 2, 'gamma': 3}
        """
        return self._new({mapping.get(k, k): v for k, v in self._data.items()})

    def diff(self, other: dict[K, V]) -> Dict[K, tuple[V | None, V | None]]:
        """
        Returns a dict of the differences between this dict and another.

        The keys of the returned dict are the keys that are not shared or have different values.
        The values are tuples containing the value from self and the value from other.

        >>> d1 = {"a": 1, "b": 2, "c": 3}
        >>> d2 = {"b": 2, "c": 4, "d": 5}
        >>> Dict(d1).diff(d2).sort()
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
        ... )
        {'a': {'score': 1, 'time': 10}, 'b': {'score': 2, 'time': 20}}
        """
        all_maps = {
            main_name: self.unwrap(),
            **{k: v for k, v in field_to_map.items()},
        }
        return Dict(mit.join_mappings(**all_maps))
