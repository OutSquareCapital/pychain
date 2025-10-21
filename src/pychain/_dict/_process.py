from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Concatenate, Self

import cytoolz as cz

from .._core import MappingWrapper


class ProcessDict[K, V](MappingWrapper[K, V]):
    def for_each[**P](
        self,
        func: Callable[Concatenate[K, V, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        """
        Apply a function to each key-value pair in the dict for side effects.

        Returns the original Dict unchanged.

        >>> import pychain as pc
        >>> pc.Dict({"a": 1, "b": 2}).for_each(
        ...     lambda k, v: print(f"Key: {k}, Value: {v}")
        ... ).unwrap()
        Key: a, Value: 1
        Key: b, Value: 2
        {'a': 1, 'b': 2}
        """
        for k, v in self.unwrap().items():
            func(k, v, *args, **kwargs)
        return self

    def update_in(
        self, *keys: K, func: Callable[[V], V], default: V | None = None
    ) -> Self:
        """
        Update value in a (potentially) nested dictionary.

        Applies the func to the value at the path specified by keys, returning a new Dict with the updated value.

        If the path does not exist, it will be created with the default value (if provided) before applying func.
        >>> import pychain as pc
        >>> inc = lambda x: x + 1
        >>> pc.Dict({"a": 0}).update_in("a", func=inc).unwrap()
        {'a': 1}
        >>> transaction = {
        ...     "name": "Alice",
        ...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> pc.Dict(transaction).update_in("purchase", "costs", func=sum).unwrap()
        {'name': 'Alice', 'purchase': {'items': ['Apple', 'Orange'], 'costs': 1.75}, 'credit card': '5555-1234-1234-1234'}
        >>> # updating a value when k0 is not in d
        >>> pc.Dict({}).update_in(1, 2, 3, func=str, default="bar").unwrap()
        {1: {2: {3: 'bar'}}}
        >>> pc.Dict({1: "foo"}).update_in(2, 3, 4, func=inc, default=0).unwrap()
        {1: 'foo', 2: {3: {4: 1}}}
        """
        return self._new(cz.dicttoolz.update_in, keys, func, default=default)

    def with_key(self, key: K, value: V) -> Self:
        """
        Return a new Dict with key set to value.

        Does not modify the initial dictionary.

        >>> import pychain as pc
        >>> pc.Dict({"x": 1}).with_key("x", 2).unwrap()
        {'x': 2}
        >>> pc.Dict({"x": 1}).with_key("y", 3).unwrap()
        {'x': 1, 'y': 3}
        >>> pc.Dict({}).with_key("x", 1).unwrap()
        {'x': 1}
        """
        return self._new(cz.dicttoolz.assoc, key, value)

    def drop(self, *keys: K) -> Self:
        """
        Return a new Dict with given keys removed.

        New dict has d[key] deleted for each supplied key.

        >>> import pychain as pc
        >>> pc.Dict({"x": 1, "y": 2}).drop("y").unwrap()
        {'x': 1}
        >>> pc.Dict({"x": 1, "y": 2}).drop("y", "x").unwrap()
        {}
        >>> pc.Dict({"x": 1}).drop("y").unwrap()  # Ignores missing keys
        {'x': 1}
        >>> pc.Dict({1: 2, 3: 4}).drop(1).unwrap()
        {3: 4}
        """
        return self._new(cz.dicttoolz.dissoc, *keys)

    def rename(self, mapping: Mapping[K, K]) -> Self:
        """
        Return a new Dict with keys renamed according to the mapping.

        Keys not in the mapping are kept as is.

        >>> import pychain as pc
        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> mapping = {"b": "beta", "c": "gamma"}
        >>> pc.Dict(d).rename(mapping).unwrap()
        {'a': 1, 'beta': 2, 'gamma': 3}
        """
        return self._new(lambda data: {mapping.get(k, k): v for k, v in data.items()})

    def sort(self, reverse: bool = False) -> Self:
        """
        Sort the dictionary by its keys and return a new Dict.

        >>> import pychain as pc
        >>> pc.Dict({"b": 2, "a": 1}).sort().unwrap()
        {'a': 1, 'b': 2}
        """
        return self._new(lambda data: dict(sorted(data.items(), reverse=reverse)))
