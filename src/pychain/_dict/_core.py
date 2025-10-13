from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz

from .._core import CommonBase

if TYPE_CHECKING:
    from .._iter import Iter


class CoreDict[K, V](CommonBase[dict[K, V]]):
    def __repr__(self) -> str:
        data_formatted: str = "\n".join(
            f"  {key!r}, {type(value).__name__}: {value!r},"
            for key, value in self._data.items()
        )
        return f"{self.__class__.__name__}(\n{data_formatted}\n)"

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        from .._iter import Iter

        return Iter(self._data.keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_values().into(list)
        [2]
        """
        from .._iter import Iter

        return Iter(self._data.values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        from .._iter import Iter

        return Iter(self._data.items())

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

    def rename(self, mapping: dict[K, K]) -> Self:
        """
        Return a new Dict with keys renamed according to the mapping.

        Keys not in the mapping are kept as is.

        >>> from pychain import Dict
        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> mapping = {"b": "beta", "c": "gamma"}
        >>> Dict(d).rename(mapping).unwrap()
        {'a': 1, 'beta': 2, 'gamma': 3}
        """
        return self._new(lambda data: {mapping.get(k, k): v for k, v in data.items()})

    def equals_to(self, other: Self | dict[Any, Any]) -> bool:
        """
        Check if two records are equal based on their data.
        """
        return (
            self._data == other._data
            if isinstance(other, CoreDict)
            else self._data == other
        )

    def sort(self, reverse: bool = False) -> Self:
        """
        Sort the dictionary by its keys and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({"b": 2, "a": 1}).sort().unwrap()
        {'a': 1, 'b': 2}
        """
        return self._new(lambda data: dict(sorted(data.items(), reverse=reverse)))

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merge other dicts into this one and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({1: "one"}).merge({2: "two"}).unwrap()
        {1: 'one', 2: 'two'}

        Later dictionaries have precedence

        >>> Dict({1: 2, 3: 4}).merge({3: 3, 4: 4}).unwrap()
        {1: 2, 3: 3, 4: 4}
        """
        return self._new(cz.dicttoolz.merge, *others)

    def merge_with(self, *others: dict[K, V], func: Callable[[Iterable[V]], V]) -> Self:
        """
        Merge dicts using a function to combine values for duplicate keys.

        A key may occur in more than one dict, and all values mapped from the key will be passed to the function as a list, such as func([val1, val2, ...]).

        >>> from pychain import Dict
        >>> Dict({1: 1, 2: 2}).merge_with({1: 10, 2: 20}, func=sum).unwrap()
        {1: 11, 2: 22}
        >>> Dict({1: 1, 2: 2}).merge_with({2: 20, 3: 30}, func=max).unwrap()
        {1: 1, 2: 20, 3: 30}

        """
        return self._new(lambda data: cz.dicttoolz.merge_with(func, data, *others))

    def flatten[U: CoreDict[str, Any]](
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

    def schema[U: CoreDict[str, Any]](self: U, max_depth: int = 2) -> U:
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

        return self.pipe_into(lambda data: _recurse_schema(data, 0))

    def filter_keys(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """
        return self._new(partial(cz.dicttoolz.keyfilter, predicate))

    def filter_keys_not(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys_not(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """

        def negate(k: K) -> bool:
            return not predicate(k)

        return self._new(partial(cz.dicttoolz.keyfilter, negate))

    def filter_values(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """
        return self._new(partial(cz.dicttoolz.valfilter, predicate))

    def filter_values_not(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values_not(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """

        def negate(v: V) -> bool:
            return not predicate(v)

        return self._new(partial(cz.dicttoolz.valfilter, negate))

    def filter_items(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items(lambda it: it[1] > 2).unwrap()
        {3: 4}
        """
        return self._new(partial(cz.dicttoolz.itemfilter, predicate))

    def filter_items_not(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items_not(lambda it: it[1] > 2).unwrap()
        {1: 2}
        """

        def negate(kv: tuple[K, V]) -> bool:
            return not predicate(kv)

        return self._new(partial(cz.dicttoolz.itemfilter, negate))

    def filter_kv(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2).unwrap()
        {3: 4}
        """

        return self._new(
            lambda data: cz.dicttoolz.itemfilter(
                lambda kv: predicate(kv[0], kv[1]), data
            )
        )

    def filter_kv_not(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv_not(lambda k, v: v > 2).unwrap()
        {1: 2}
        """

        return self._new(
            lambda data: cz.dicttoolz.itemfilter(
                lambda kv: not predicate(kv[0], kv[1]), data
            )
        )
