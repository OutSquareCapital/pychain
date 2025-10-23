from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import TYPE_CHECKING, Any, Concatenate

import cytoolz as cz

from .._core import MappingWrapper

if TYPE_CHECKING:
    from .._dict import Dict


class NestedDict[K, V](MappingWrapper[K, V]):
    def struct[**P, R, U: dict[Any, Any]](
        self: NestedDict[K, U],
        func: Callable[Concatenate[Dict[K, U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[K, R]:
        """
        Apply a function to each value after wrapping it in a Dict.

        Args:
            func: Function to apply to each value after wrapping it in a Dict.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Syntactic sugar for `map_values(lambda data: func(pc.Dict(data), *args, **kwargs))`
        ```python
        >>> import pyochain as pc
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

        ```
        """
        from ._main import Dict

        def _struct(data: Mapping[K, U]) -> dict[K, R]:
            def _(v: dict[Any, Any]) -> R:
                return func(Dict(v), *args, **kwargs)

            return cz.dicttoolz.valmap(_, data)

        return self.apply(_struct)

    def flatten(
        self: NestedDict[str, Any], sep: str = ".", max_depth: int | None = None
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary, concatenating keys with the specified separator.

        Args:
            sep: Separator to use when concatenating keys
            max_depth: Maximum depth to flatten. If None, flattens completely.
        ```python
        >>> import pyochain as pc
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

        ```
        """

        def _flatten(
            d: dict[Any, Any], parent_key: str = "", current_depth: int = 1
        ) -> dict[str, Any]:
            items: list[tuple[str, Any]] = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, dict) and (
                    max_depth is None or current_depth < max_depth + 1
                ):
                    items.extend(
                        _flatten(v, new_key, current_depth + 1).items()  # type: ignore
                    )
                else:
                    items.append((new_key, v))  # type: ignore
            return dict(items)

        return self.apply(_flatten)

    def with_nested_key(self, *keys: K, value: V) -> Dict[K, V]:
        """
        Set a nested key path and return a new Dict with new, potentially nested, key value pair.

        Args:
            *keys: Sequence of keys representing the nested path.
            value: Value to set at the specified nested path.
        ```python
        >>> import pyochain as pc
        >>> purchase = {
        ...     "name": "Alice",
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ...     "credit card": "5555-1234-1234-1234",
        ... }
        >>> pc.Dict(purchase).with_nested_key(
        ...     "order", "costs", value=[0.25, 1.00]
        ... ).unwrap()
        {'name': 'Alice', 'order': {'items': ['Apple', 'Orange'], 'costs': [0.25, 1.0]}, 'credit card': '5555-1234-1234-1234'}

        ```
        """
        return self.apply(cz.dicttoolz.assoc_in, keys, value=value)

    def schema(self, max_depth: int = 1) -> Dict[str, Any]:
        """
        Return the schema of the dictionary up to a maximum depth.

        Args:
            max_depth: Maximum depth to inspect. Nested dicts beyond this depth are marked as 'dict'.

        When the max depth is reached, nested dicts are marked as 'dict'.
        For lists, only the first element is inspected.
        ```python
        >>> import pyochain as pc
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

        ```
        """

        def _schema(data: dict[Any, Any]) -> Any:
            def _recurse_schema(node: Any, current_depth: int) -> Any:
                if isinstance(node, dict):
                    if current_depth >= max_depth:
                        return "dict"
                    return {
                        k: _recurse_schema(v, current_depth + 1)
                        for k, v in node.items()  # type: ignore
                    }
                elif cz.itertoolz.isiterable(node):
                    if current_depth >= max_depth:
                        return type(node).__name__
                    return _recurse_schema(cz.itertoolz.first(node), current_depth + 1)
                else:
                    return type(node).__name__

            return _recurse_schema(data, 0)

        return self.apply(_schema)

    def pluck[U: str | int](self: NestedDict[U, Any], *keys: str) -> Dict[U, Any]:
        """
        Extract values from nested dictionaries using a sequence of keys.

        Args:
            *keys: Sequence of keys to extract values from the nested dictionaries.
        ```python
        >>> import pyochain as pc
        >>> data = {
        ...     "person1": {"name": "Alice", "age": 30},
        ...     "person2": {"name": "Bob", "age": 25},
        ... }
        >>> pc.Dict(data).pluck("name").unwrap()
        {'person1': 'Alice', 'person2': 'Bob'}

        ```
        """

        getter = partial(cz.dicttoolz.get_in, keys)

        def _pluck(data: Mapping[U, Any]) -> dict[U, Any]:
            return cz.dicttoolz.valmap(getter, data)

        return self.apply(_pluck)

    def get_in(self, *keys: K, default: Any = None) -> Any:
        """
        Retrieve a value from a nested dictionary structure.

        Args:
            *keys: Sequence of keys representing the nested path to retrieve the value.
            default: Default value to return if the keys do not exist.

        ```python
        >>> import pyochain as pc
        >>> data = {"a": {"b": {"c": 1}}}
        >>> pc.Dict(data).get_in("a", "b", "c")
        1
        >>> pc.Dict(data).get_in("a", "x", default="Not Found")
        'Not Found'

        ```
        """

        def _get_in(data: Mapping[K, V]) -> Any:
            return cz.dicttoolz.get_in(keys, data, default)

        return self.into(_get_in)
