from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Self, overload

import cytoolz as cz

from .._core import CommonBase, Wrapper, dict_factory

if TYPE_CHECKING:
    from ._main import Dict


class NestedDict[K, V](CommonBase[dict[K, V]]):
    @overload
    def get_nested(self, *keys: K, default: V) -> Wrapper[V]: ...
    @overload
    def get_nested[T](self, *keys: K, default: T) -> Wrapper[V | T]: ...
    @overload
    def get_nested(self, *keys: K) -> Wrapper[V | None]: ...

    def get_nested[T](self, *keys: K, default: T = None) -> Wrapper[V | T]:
        """
        Get a value from a nested dictionary.

        Returns the value at the path specified by keys. If the path does not exist, returns the default value. This is a terminal operation.

        >>> from pychain import Dict
        >>> purchase = {
        ...     "user": {"name": "Alice"},
        ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
        ... }
        >>> Dict(purchase).get_nested("order", "costs")
        [0.5, 1.25]
        >>> Dict(purchase).get_nested("user", "age", default=99)
        99
        """
        return Wrapper(cz.dicttoolz.get_in(keys, self._data, default))

    def schema(self, max_depth: int = 2) -> Dict[K, Any]:
        """
        Return the schema of the dictionary up to a maximum depth.
        When the max depth is reached, nested dicts are marked as 'dict'.
        For lists, only the first element is inspected.

        >>> from pychain import Dict
        >>> # Depth 2: we see up to level2
        >>> data = {"level1": {"level2": {"level3": {"key": "value"}}}}
        >>> Dict(data).schema()
        {'level1': {'level2': 'dict'}}
        >>>
        >>> # Depth 3: we see up to level3
        >>> Dict(data).schema(max_depth=3)
        {'level1': {'level2': {'level3': 'dict'}}}
        """

        def get_structure(node: Any, current_depth: int) -> Any:
            match node:
                case dict():
                    if current_depth >= max_depth:
                        return "dict"
                    return {
                        k: get_structure(v, current_depth + 1)
                        for k, v in node.items()  # type: ignore
                    }
                case list():
                    if node:
                        return []
                    return [get_structure(node[0])]  # type: ignore
                case _:
                    return type(node).__name__

        return dict_factory(get_structure(self._data, 0))

    def select_nested[KD, VD](
        self, *keys: K, kdtype: KD = Any, vdtype: VD = Any
    ) -> Dict[KD, VD]:
        """
        Select a nested dictionary at the path specified by keys.

        You can optionally specify the expected types for keys and values of the nested dictionary.

        Those types are only used for type hinting and are not enforced at runtime.

        >>> from pychain import Dict
        >>> data = {"config": {"params": {"retries": 3}}}
        >>> Dict(data).select_nested("config", "params").get_value("retries")
        3
        """
        nested_val = cz.dicttoolz.get_in(keys, self._data)  # type: ignore
        if not isinstance(nested_val, dict):
            raise TypeError(
                f"La valeur à la clé '{keys[-1]}' n'est pas un dictionnaire, "
                f"mais de type '{type(nested_val).__name__}'."
            )

        return dict_factory(nested_val)  # type: ignore

    def update_in(
        self, *keys: K, func: Callable[[V], V], default: V | None = None
    ) -> Self:
        """
        Update value in a (potentially) nested dictionary.

        Applies the func to the value at the path specified by keys, returning a new Dict with the updated value.

        If the path does not exist, it will be created with the default value (if provided) before applying func.

        >>> from pychain import Dict
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

    def flatten_keys(
        self: CommonBase[dict[str, Any]], sep: str = ".", max_depth: int | None = None
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary, concatenating keys with the specified separator.

        Args:
            sep: Separator to use when concatenating keys
            max_depth: Maximum depth to flatten. If None, flattens completely.

        >>> from pychain import Dict
        >>> data = {
        ...     "config": {"params": {"retries": 3, "timeout": 30}, "mode": "fast"},
        ...     "version": 1.0,
        ... }
        >>> Dict(data).flatten_keys()
        {'config.params.retries': 3, 'config.params.timeout': 30, 'config.mode': 'fast', 'version': 1.0}
        >>> Dict(data).flatten_keys(sep="_")
        {'config_params_retries': 3, 'config_params_timeout': 30, 'config_mode': 'fast', 'version': 1.0}
        >>> Dict(data).flatten_keys(max_depth=1)
        {'config.params': {'retries': 3, 'timeout': 30}, 'config.mode': 'fast', 'version': 1.0}

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
                    items.extend(_flatten(v, new_key, current_depth + 1).items())  # type: ignore
                else:
                    items.append((new_key, v))  # type: ignore
            return dict(items)

        return dict_factory(_flatten(self._data))
