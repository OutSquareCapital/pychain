from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self, overload

import cytoolz as cz

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._core import Iter


class Dict[K, V](CommonBase[dict[K, V]]):
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

    # BUILTINS------------------------------------------------------------------
    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

            >>> Dict({1: 2}).iter_keys().to_list()
            [1]
        """
        return iter_factory(self._data.keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

            >>> Dict({1: 2}).iter_values().to_list()
            [2]
        """
        return iter_factory(self._data.values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

            >>> Dict({1: 2}).iter_items().to_list()
            [(1, 2)]
        """
        return iter_factory(self._data.items())

    def copy(self) -> Self:
        """Return a shallow copy of the dict."""
        return self._new(self._data.copy())

    def update(self, *others: dict[K, V]) -> Self:
        """
        Update the dict with other(s) dict(s) and return self for convenience.

        **Warning** ⚠️

        This modifies the dict in place.

            >>> Dict({1: 2}).update({3: 4})
            {1: 2, 3: 4}
        """
        self._data.update(*others)
        return self

    @overload
    def get_value(self, key: K, default: None = None) -> V | None: ...
    @overload
    def get_value(self, key: K, default: V = ...) -> V: ...
    def get_value(self, key: K, default: V | None = None) -> V | None:
        """Get the value for a key, returning default if not found."""
        return self._data.get(key, default)

    def set_value(self, key: K, value: V) -> Self:
        """
        Set the value for a key and return self for convenience.

        **Warning** ⚠️

        This modifies the dict in place.

        >>> Dict({}).set_value("x", 1)
        {'x': 1}
        """
        self._data[key] = value
        return self

    # CYTOOLZ------------------------------------------------------------------
    def filter_keys(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys(lambda x: x % 2 == 0)
        {2: 3, 4: 5}
        """
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_values(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values(lambda x: x % 2 == 0)
        {1: 2, 3: 4}
        """
        return self._new(cz.dicttoolz.valfilter(predicate, self._data))

    def filter_items(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> Dict({1: 2, 3: 4}).filter_items(lambda it: it[1] > 2)
        {3: 4}
        """
        return self._new(cz.dicttoolz.itemfilter(predicate, self._data))

    def filter_kv(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2)
        {3: 4}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: predicate(kv[0], kv[1]), self._data)
        )

    def with_key(self, key: K, value: V) -> Self:
        """
        Return a new Dict with key set to value.

        >>> Dict({"x": 1}).with_key("x", 2)
        {'x': 2}
        >>> Dict({"x": 1}).with_key("y", 3)
        {'x': 1, 'y': 3}
        >>> Dict({}).with_key("x", 1)
        {'x': 1}
        """
        return self._new(cz.dicttoolz.assoc(self._data, key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        """
        Set a nested key path and return a new Dict with new, potentially nested, key value pair

        >>> purchase = {
        ...     "name": "Alice",
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> Dict(purchase).with_nested_key(["order", "costs"], [0.25, 1.00])
        {'name': 'Alice', 'order': {'items': ['Apple', 'Orange'], 'costs': [0.25, 1.0]}, 'credit card': '5555-1234-1234-1234'}
        """
        return self._new(cz.dicttoolz.assoc_in(self._data, keys=keys, value=value))

    def update_in(
        self, keys: Iterable[K], func: Callable[[V], V], default: V | None = None
    ) -> Self:
        """
        Update value in a (potentially) nested dictionary

        inputs: d - dictionary on which to operate keys - list or tuple giving the location of the value to be changed in d func - function to operate on that value

        If keys == [k0,..,kX] and d[k0]..[kX] == v, update_in returns a copy of the original dictionary with v replaced by func(v), but does not mutate the original dictionary.

        If k0 is not a key in d, update_in creates nested dictionaries to the depth specified by the keys, with the innermost value set to func(default).

        >>> inc = lambda x: x + 1
        >>> Dict({"a": 0}).update_in(["a"], func=inc)
        {'a': 1}
        >>> transaction = {
        ...     "name": "Alice",
        ...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> Dict(transaction).update_in(["purchase", "costs"], func=sum)
        {'name': 'Alice', 'purchase': {'items': ['Apple', 'Orange'], 'costs': 1.75}, 'credit card': '5555-1234-1234-1234'}
        >>> # updating a value when k0 is not in d
        >>> Dict({}).update_in([1, 2, 3], func=str, default="bar")
        {1: {2: {3: 'bar'}}}
        >>> Dict({1: "foo"}).update_in([2, 3, 4], func=inc, default=0)
        {1: 'foo', 2: {3: {4: 1}}}

        """
        return self._new(
            cz.dicttoolz.update_in(self._data, keys=keys, func=func, default=default)
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

        >>> Dict({"Alice": 10, "Bob": 20}).map_items(reversed)
        {10: 'Alice', 20: 'Bob'}
        """
        return Dict(cz.dicttoolz.itemmap(func, self._data))

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
