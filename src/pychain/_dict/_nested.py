from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import TYPE_CHECKING, Any, Concatenate

import cytoolz as cz

from .._core import MappingWrapper
from ._funcs import flatten_recursive, schema_recursive

if TYPE_CHECKING:
    from .._dict import Dict


class NestedDict[K, V](MappingWrapper[K, V]):
    def struct[**P, R, U: Mapping[Any, Any]](
        self: NestedDict[K, U],
        func: Callable[Concatenate[Dict[K, U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[K, R]:
        """
        Apply a function to each value after wrapping it in a Dict.

        Syntactic sugar for ``map_values(lambda data: func(pc.Dict(data), *args, **kwargs))``
        >>> import pychain as pc
        >>> data = {
        ...     "person1": {"name": "Alice", "age": 30, "city": "New York"},
        ...     "person2": {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ... }
        >>> pc.Dict(data).struct(lambda d: d.map_keys(str.upper).drop("AGE").unwrap())
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            'person1': {'NAME': 'Alice', 'CITY': 'New York'},
            'person2': {'NAME': 'Bob', 'CITY': 'Los Angeles'}
        })
        """
        from ._main import Dict

        return self.apply(
            lambda data: cz.dicttoolz.valmap(
                lambda v: func(Dict(v), *args, **kwargs), data
            )
        )

    def flatten(
        self: NestedDict[str, Any], sep: str = ".", max_depth: int | None = None
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
        return self.apply(flatten_recursive, sep=sep, max_depth=max_depth)

    def with_nested_key(self, *keys: K, value: V) -> Dict[K, V]:
        """
        Set a nested key path and return a new Dict with new, potentially nested, key value pair.

        >>> from pychain import Dict
        >>> purchase = {
        ...     "name": "Alice",
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> Dict(purchase).with_nested_key(
        ...     "order", "costs", value=[0.25, 1.00]
        ... ).unwrap()
        {'name': 'Alice', 'order': {'items': ['Apple', 'Orange'], 'costs': [0.25, 1.0]}, 'credit card': '5555-1234-1234-1234'}
        """
        return self.apply(cz.dicttoolz.assoc_in, keys, value=value)

    def schema(self, max_depth: int = 1) -> Dict[str, Any]:
        """
        Return the schema of the dictionary up to a maximum depth.
        When the max depth is reached, nested dicts are marked as 'dict'.
        For lists, only the first element is inspected.

        >>> import pychain as pc
        >>> # Depth 2: we see up to level2
        >>> data = {
        ...     "level1": {"level2": {"level3": {"key": "value"}}},
        ...     "other_key": 123,
        ...     "list_key": [{"sub_key": "sub_value"}],
        ... }
        >>> pc.Dict(data).schema(max_depth=1).unwrap()
        {'level1': 'dict', 'other_key': 'int', 'list_key': 'list'}

        >>> pc.Dict(data).schema(max_depth=2).unwrap()
        {'level1': {'level2': 'dict'}, 'other_key': 'int', 'list_key': 'dict'}
        >>>
        >>> # Depth 3: we see up to level3
        >>> pc.Dict(data).schema(max_depth=3).unwrap()
        {'level1': {'level2': {'level3': 'dict'}}, 'other_key': 'int', 'list_key': {'sub_key': 'str'}}
        """
        return self.apply(schema_recursive, max_depth=max_depth)

    def pluck[U: str | int](self: NestedDict[U, Any], *keys: str) -> Dict[U, Any]:
        """

        >>> import pychain as pc
        >>> data = {
        ...     "person1": {"name": "Alice", "age": 30},
        ...     "person2": {"name": "Bob", "age": 25},
        ... }
        >>> pc.Dict(data).pluck("name").unwrap()
        {'person1': 'Alice', 'person2': 'Bob'}
        """
        getter = partial(cz.dicttoolz.get_in, keys)
        return self.apply(lambda data: cz.dicttoolz.valmap(getter, data))
