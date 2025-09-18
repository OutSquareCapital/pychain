from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import iter_factory

if TYPE_CHECKING:
    from .._core import Iter


@dataclass(slots=True)
class StructNameSpace[K, V]:
    """Namespace for struct (dict) methods."""

    _parent: Iterable[dict[K, V]]

    def iter_values(self) -> Iter[V]:
        """
        Iterate over the values in the dicts.

        >>> from pychain import Iter
        >>> data = [{"a": 1, "b": 2}, {"c": 3}]
        >>> Iter(data).struct.iter_values().to_list()
        [1, 2, 3]
        >>> nested_data = [{"a": [1, 2]}, {"b": [3, 4]}]
        >>> Iter(nested_data).struct.iter_values().to_list()
        [[1, 2], [3, 4]]
        """
        return iter_factory(v for d in self._parent for v in d.values())

    def iter_keys(self) -> Iter[K]:
        """
        Iterate over the keys in the dicts.

        >>> from pychain import Iter
        >>> data = [{"a": 1, "b": 2}, {"c": 3}]
        >>> Iter(data).struct.iter_keys().to_list()
        ['a', 'b', 'c']
        """
        return iter_factory(k for d in self._parent for k in d.keys())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Iterate over the (key, value) pairs in the dicts.
        Useful for flattening an iterable of dicts into an iterable of key-value pairs.

        >>> from pychain import Iter
        >>> data = [{"a": 1, "b": 2}, {"c": 3}]
        >>> Iter(data).struct.iter_items().to_list()
        [('a', 1), ('b', 2), ('c', 3)]
        """
        return iter_factory(it for d in self._parent for it in d.items())

    def filter_keys(self, predicate: Callable[[K], bool]) -> Iter[dict[K, V]]:
        """
        Return a new Iter containing dicts with keys that satisfy predicate.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.filter_keys(lambda k: k == "a").to_list()
            [{'a': 1}, {}]
        """
        return iter_factory(cz.dicttoolz.keyfilter(predicate, d) for d in self._parent)

    def filter_values(self, predicate: Callable[[V], bool]) -> Iter[dict[K, V]]:
        """
        Return a new Iter containing dicts with values that satisfy predicate.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.filter_values(lambda v: v > 1).to_list()
            [{'b': 2}, {'c': 3}]
        """
        return iter_factory(cz.dicttoolz.valfilter(predicate, d) for d in self._parent)

    def filter_items(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Iter[dict[K, V]]:
        """
        Filter items by predicate applied to (key, value) tuples.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
            >>> Iter(data).struct.filter_items(lambda it: it[1] > 2).to_list()
            [{}, {'c': 3, 'd': 4}]
        """
        return iter_factory(cz.dicttoolz.itemfilter(predicate, d) for d in self._parent)

    def filter_kv(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Iter[dict[K, V]]:
        """
        Filter items by predicate applied to key and value as separate arguments.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
            >>> Iter(data).struct.filter_kv(lambda k, v: v > 2).to_list()
            [{}, {'c': 3, 'd': 4}]
        """
        return iter_factory(
            cz.dicttoolz.itemfilter(lambda kv: predicate(kv[0], kv[1]), d)
            for d in self._parent
        )

    def with_key(self, key: K, value: V) -> Iter[dict[K, V]]:
        """
        Return a new Iter with key set to value in each dict.

            >>> from pychain import Iter
            >>> data = [{"x": 1}, {"y": 2}]
            >>> Iter(data).struct.with_key("z", 3).to_list()
            [{'x': 1, 'z': 3}, {'y': 2, 'z': 3}]
        """
        return iter_factory(
            cz.dicttoolz.assoc(d, key=key, value=value) for d in self._parent
        )

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Iter[dict[K, V]]:
        """
        Set a nested key path and return a new Iter with new, potentially nested, key value pair in each dict.

            >>> from pychain import Iter
            >>> data = [
            ...     {
            ...         "name": "Alice",
            ...         "order": {"items": ["Apple"], "costs": [0.50]},
            ...     },
            ...     {
            ...         "name": "Bob",
            ...         "order": {"items": ["Orange"], "costs": [1.25]},
            ...     },
            ... ]
            >>> Iter(data).struct.with_nested_key(["order", "costs"], [0.25]).to_list()
            [{'name': 'Alice', 'order': {'items': ['Apple'], 'costs': [0.25]}}, {'name': 'Bob', 'order': {'items': ['Orange'], 'costs': [0.25]}}]
        """
        return iter_factory(
            cz.dicttoolz.assoc_in(d, keys=keys, value=value) for d in self._parent
        )

    def update_in(
        self, keys: Iterable[K], func: Callable[[V], V], default: V | None = None
    ) -> Iter[dict[K, V]]:
        """
        Update value in a (potentially) nested dictionary for each dict in the iter.

            >>> from pychain import Iter
            >>> data = [
            ...     {
            ...         "name": "Alice",
            ...         "purchase": {"items": ["Apple"], "costs": [0.50]},
            ...     },
            ...     {
            ...         "name": "Bob",
            ...         "purchase": {"items": ["Orange"], "costs": [1.25]},
            ...     },
            ... ]
            >>> Iter(data).struct.update_in(["purchase", "costs"], func=sum).to_list()
            [{'name': 'Alice', 'purchase': {'items': ['Apple'], 'costs': 0.5}}, {'name': 'Bob', 'purchase': {'items': ['Orange'], 'costs': 1.25}}]
        """
        return iter_factory(
            cz.dicttoolz.update_in(d, keys=keys, func=func, default=default)
            for d in self._parent
        )

    def merge(self, *others: dict[K, V]) -> Iter[dict[K, V]]:
        """
        Merge other dicts into each dict in the iter and return a new Iter.

            >>> from pychain import Iter
            >>> data = [{"a": 1}, {"b": 2}]
            >>> Iter(data).struct.merge({"c": 3}).to_list()
            [{'a': 1, 'c': 3}, {'b': 2, 'c': 3}]
        """
        return iter_factory(cz.dicttoolz.merge(d, *others) for d in self._parent)

    def merge_with(
        self, *others: dict[K, V], func: Callable[[Iterable[V]], V]
    ) -> Iter[dict[K, V]]:
        """
        Merge dicts using a function to combine values for duplicate keys.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
            >>> Iter(data).struct.merge_with({"a": 10, "c": 30}, func=sum).to_list()
            [{'a': 11, 'b': 2, 'c': 30}, {'c': 33, 'd': 4, 'a': 10}]
        """
        return iter_factory(
            cz.dicttoolz.merge_with(func, d, *others) for d in self._parent
        )

    def drop(self, *keys: K) -> Iter[dict[K, V]]:
        """
        Return a new Iter with given keys removed from each dict.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
            >>> Iter(data).struct.drop("a", "c").to_list()
            [{'b': 2}, {'d': 4}]
        """
        return iter_factory(cz.dicttoolz.dissoc(d, *keys) for d in self._parent)

    def map_keys[T](self, func: Callable[[K], T]) -> Iter[dict[T, V]]:
        """
        Return an Iter with keys transformed by func for each dict.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.map_keys(str.upper).to_list()
            [{'A': 1, 'B': 2}, {'C': 3}]
        """
        return iter_factory(cz.dicttoolz.keymap(func, d) for d in self._parent)

    def map_values[T](self, func: Callable[[V], T]) -> Iter[dict[K, T]]:
        """
        Return an Iter with values transformed by func for each dict.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.map_values(lambda v: v * 10).to_list()
            [{'a': 10, 'b': 20}, {'c': 30}]
        """
        return iter_factory(cz.dicttoolz.valmap(func, d) for d in self._parent)

    def map_items[KR, VR](
        self,
        func: Callable[[tuple[K, V]], tuple[KR, VR]],
    ) -> Iter[dict[KR, VR]]:
        """
        Transform (key, value) pairs using a function that takes a (key, value) tuple for each dict.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.map_items(
            ...     lambda kv: (kv[0].upper(), kv[1] * 10)
            ... ).to_list()
            [{'A': 10, 'B': 20}, {'C': 30}]
        """
        return iter_factory(cz.dicttoolz.itemmap(func, d) for d in self._parent)

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Iter[dict[KR, VR]]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments for each dict.

            >>> from pychain import Iter
            >>> data = [{"a": 1, "b": 2}, {"c": 3}]
            >>> Iter(data).struct.map_kv(lambda k, v: (k.upper(), v * 10)).to_list()
            [{'A': 10, 'B': 20}, {'C': 30}]
        """
        return iter_factory(
            cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), d) for d in self._parent
        )
