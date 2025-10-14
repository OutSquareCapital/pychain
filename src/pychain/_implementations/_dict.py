from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any, Concatenate, Self

import cytoolz as cz

from .._core import SupportsKeysAndGetItem
from .._executors import BaseStruct
from ._expr import IntoExpr, parse_expr

if TYPE_CHECKING:
    from ._iter import Iter


class Dict[K, V](BaseStruct[K, V]):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    def _from_context(self, plan: Iterable[IntoExpr], is_selection: bool) -> Self:
        def _(data: dict[K, V]) -> dict[K, V]:
            if is_selection:
                result_dict: dict[K, V] = {}
            else:
                result_dict = data.copy()

            for expr in plan:
                parse_expr(expr).__compute__(data, result_dict)

            return result_dict

        return self._new(_)

    def select(self, *exprs: IntoExpr) -> Self:
        """
        Select only the specified fields, creating a new dictionary with just those fields.
        """
        return self._from_context(exprs, True)

    def with_fields(self, *exprs: IntoExpr) -> Self:
        """
        Adds or replaces fields in the existing dictionary.
        """
        return self._from_context(exprs, False)

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
        return Dict(self.into(func, *args, **kwargs))

    def __init__(self, data: SupportsKeysAndGetItem[K, V] | dict[K, V]) -> None:
        if not isinstance(data, dict):
            data = dict(data)
        super().__init__(data)

    def __repr__(self) -> str:
        data_formatted: str = "\n".join(
            f"  {key!r}, {type(value).__name__}: {value!r},"
            for key, value in self.unwrap().items()
        )
        return f"{self.__class__.__name__}(\n{data_formatted}\n)"

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        from ._iter import Iter

        return Iter(self.unwrap().keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_values().into(list)
        [2]
        """
        from ._iter import Iter

        return Iter(self.unwrap().values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        from ._iter import Iter

        return Iter(self.unwrap().items())

    def equals_to(self, other: Self | dict[Any, Any] | Mapping[Any, Any]) -> bool:
        """
        Check if two records are equal based on their data.
        """
        return (
            self.unwrap() == other.unwrap()
            if isinstance(other, Dict)
            else self.unwrap() == other
        )

    def flatten[U: Dict[str, Any]](
        self: U, sep: str = ".", max_depth: int | None = None
    ) -> U:
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

        def _recurse_flatten(
            d: dict[Any, Any], parent_key: str = "", current_depth: int = 1
        ) -> dict[str, Any]:
            items: list[tuple[str, Any]] = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, dict) and (
                    max_depth is None or current_depth < max_depth + 1
                ):
                    items.extend(
                        _recurse_flatten(v, new_key, current_depth + 1).items()  # type: ignore
                    )
                else:
                    items.append((new_key, v))  # type: ignore
            return dict(items)

        return self._new(lambda data: _recurse_flatten(data))

    def schema(self, max_depth: int = 2) -> Dict[str, Any]:
        """
        Return the schema of the dictionary up to a maximum depth.
        When the max depth is reached, nested dicts are marked as 'dict'.
        For lists, only the first element is inspected.

        >>> import pychain as pc
        >>> # Depth 2: we see up to level2
        >>> data = {"level1": {"level2": {"level3": {"key": "value"}}}}
        >>> pc.Dict(data).schema().unwrap()
        {'level1': {'level2': 'dict'}}
        >>>
        >>> # Depth 3: we see up to level3
        >>> pc.Dict(data).schema(max_depth=3).unwrap()
        {'level1': {'level2': {'level3': 'dict'}}}
        """

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

        return self.apply(lambda data: _recurse_schema(data, 0))

    def implode(self) -> Dict[K, Iterable[V]]:
        """
        Nest all the values in lists.
        syntactic sugar for map_values(lambda v: [v])

        >>> Dict({1: 2, 3: 4}).implode().unwrap()
        {1: [2], 3: [4]}
        """
        return self.map_values(lambda v: [v])

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
