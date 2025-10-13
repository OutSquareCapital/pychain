from collections.abc import Callable, Iterable
from typing import Any

import cytoolz as cz
import more_itertools as mit


def filter_items[K, V](
    data: dict[K, V], predicate: Callable[[tuple[K, V]], bool]
) -> dict[K, V]:
    return cz.dicttoolz.itemfilter(predicate, data)


def filter_values[K, V](data: dict[K, V], predicate: Callable[[V], bool]) -> dict[K, V]:
    return cz.dicttoolz.valfilter(predicate, data)


def filter_keys[K, V](data: dict[K, V], predicate: Callable[[K], bool]) -> dict[K, V]:
    return cz.dicttoolz.keyfilter(predicate, data)


def map_keys[K, V, T](data: dict[K, V], func: Callable[[K], T]) -> dict[T, V]:
    return cz.dicttoolz.keymap(func, data)


def map_values[K, V, T](data: dict[K, V], func: Callable[[V], T]) -> dict[K, T]:
    return cz.dicttoolz.valmap(func, data)


def merge_with[K, V](
    data: dict[K, V], more_data: Iterable[dict[K, V]], func: Callable[[Iterable[V]], V]
) -> dict[K, V]:
    return cz.dicttoolz.merge_with(func, data, *more_data)


def map_items[K, V, KR, VR](
    data: dict[K, V],
    func: Callable[[tuple[K, V]], tuple[KR, VR]],
) -> dict[KR, VR]:
    return cz.dicttoolz.itemmap(func, data)


def map_kv[K, V, KR, VR](
    data: dict[K, V],
    func: Callable[[K, V], tuple[KR, VR]],
) -> dict[KR, VR]:
    def _(kv: tuple[K, V]) -> tuple[KR, VR]:
        return func(kv[0], kv[1])

    return cz.dicttoolz.itemmap(_, data)


def reverse[K, V](data: dict[K, V]) -> dict[V, K]:
    return cz.dicttoolz.itemmap(reversed, data)


def flip_item[K, V](data: dict[K, V]) -> dict[V, list[K]]:
    flipped: dict[V, list[K]] = {}
    for key, value in data.items():
        if value in flipped:
            flipped[value].append(key)
        else:
            flipped[value] = [key]
    return flipped


def diff[K, V](
    data: dict[K, V], other: dict[K, V]
) -> dict[K, tuple[V | None, V | None]]:
    all_keys: set[K] = data.keys() | other.keys()
    diffs: dict[K, tuple[V | None, V | None]] = {}
    for key in all_keys:
        self_val = data.get(key)
        other_val = other.get(key)
        if self_val != other_val:
            diffs[key] = (self_val, other_val)
    return diffs


def join_mapping[K, V](
    data: dict[K, V], main_name: str = "main", **field_to_map: dict[K, V]
) -> dict[K, dict[str, V]]:
    all_maps: dict[str, dict[K, V]] = {
        main_name: data,
        **{k: v for k, v in field_to_map.items()},
    }
    return mit.join_mappings(**all_maps)


def flatten(
    data: dict[str, Any], sep: str = ".", max_depth: int | None = None
) -> dict[str, Any]:
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

    return _recurse_flatten(data)


def schema(
    data: dict[str, Any], max_depth: int = 2
) -> Callable[[dict[str, Any]], dict[str, Any]]:
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

    def get_structure(node: Any, current_depth: int) -> Any:
        if isinstance(node, dict):
            if current_depth >= max_depth:
                return "dict"
            return {
                k: get_structure(v, current_depth + 1)
                for k, v in node.items()  # type: ignore
            }
        elif cz.itertoolz.isiterable(node):
            if current_depth >= max_depth:
                return type(node).__name__
            return get_structure(cz.itertoolz.first(node), current_depth + 1)
        else:
            return type(node).__name__

    return get_structure(data, current_depth=0)


def rename[K, V](data: dict[K, V], mapping: dict[K, K]) -> dict[K, V]:
    return {mapping.get(k, k): v for k, v in data.items()}


def sort_keys[K, V](data: dict[K, V], reverse: bool) -> dict[K, V]:
    return dict(sorted(data.items(), reverse=reverse))
