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
