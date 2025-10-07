from collections.abc import Callable
from typing import Self, overload

import cytoolz as cz

from .._core import CommonBase


class ProcessDict[K, V](CommonBase[dict[K, V]]):
    def copy(self) -> Self:
        """Return a shallow copy of the dict."""
        return self._new(self._data.copy())

    def update(self, *others: dict[K, V]) -> Self:
        """
        Update the dict with other(s) dict(s) and return self for convenience.

        **Warning** ⚠️

        This modifies the dict in place.

        >>> from pychain import Dict
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

        >>> from pychain import Dict
        >>> Dict({}).set_value("x", 1)
        {'x': 1}
        """
        self._data[key] = value
        return self

    def select_keys(self, *keys: K) -> Self:
        """
        Return a new Dict containing only the specified keys.

        Keys that are not in the original dict are ignored.

        >>> from pychain import Dict
        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> Dict(d).select_keys("a", "c", "d")
        {'a': 1, 'c': 3}
        """
        return self._new({k: v for k, v in self._data.items() if k in set(keys)})

    def filter_keys(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys(lambda x: x % 2 == 0)
        {2: 3, 4: 5}
        """
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_values(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

        >>> from pychain import Dict
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

        >>> from pychain import Dict
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

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2)
        {3: 4}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: predicate(kv[0], kv[1]), self._data)
        )

    def with_key(self, key: K, value: V) -> Self:
        """
        Return a new Dict with key set to value.

        >>> from pychain import Dict
        >>> Dict({"x": 1}).with_key("x", 2)
        {'x': 2}
        >>> Dict({"x": 1}).with_key("y", 3)
        {'x': 1, 'y': 3}
        >>> Dict({}).with_key("x", 1)
        {'x': 1}
        """
        return self._new(cz.dicttoolz.assoc(self._data, key=key, value=value))

    def with_nested_key(self, *keys: K, value: V) -> Self:
        """
        Set a nested key path and return a new Dict with new, potentially nested, key value pair.

        >>> from pychain import Dict
        >>> purchase = {
        ...     "name": "Alice",
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> Dict(purchase).with_nested_key("order", "costs", value=[0.25, 1.00])
        {'name': 'Alice', 'order': {'items': ['Apple', 'Orange'], 'costs': [0.25, 1.0]}, 'credit card': '5555-1234-1234-1234'}
        """
        return self._new(cz.dicttoolz.assoc_in(self._data, keys, value=value))

    def sort(self, reverse: bool = False) -> Self:
        """
        Sort the dictionary by its keys and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({"b": 2, "a": 1}).sort()
        {'a': 1, 'b': 2}
        """
        return self._new(dict(sorted(self._data.items(), reverse=reverse)))
