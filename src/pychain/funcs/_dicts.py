from collections.abc import Callable, Iterable
from functools import partial
from typing import Any

import cytoolz.dicttoolz as dcz

from .._protocols import CheckFunc, ProcessFunc, TransformFunc


def _merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    return dcz.merge(on, *others)


def _drop[K, V](data: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return dcz.dissoc(data, *keys)


def _flatten_recursive[V](
    d: dict[Any, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    items: dict[str, V] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(_flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items


def filter_on_key[K, V](
    key: K, predicate: CheckFunc[V]
) -> Callable[[dict[K, V]], dict[K, V]]:
    """
    Crée une fonction qui applique un prédicat à la valeur d'une clé spécifique
    dans un dictionnaire, en ne supprimant l'élément que si le prédicat est faux.
    Les autres paires clé-valeur ne sont pas affectées.
    """

    def predicate_for_itemfilter(item: tuple[K, V]) -> bool:
        current_key, current_value = item
        if current_key != key:
            return True
        return predicate(current_value)

    return filter_items(predicate_for_itemfilter)


def map_items[K, V, K1, V1](
    f: TransformFunc[tuple[K, V], tuple[K1, V1]],
) -> partial[dict[K1, V1]]:
    return partial(dcz.itemmap, f)


def map_keys[K, K1](f: TransformFunc[K, K1]) -> partial[dict[K1, Any]]:
    return partial(dcz.keymap, f)


def map_values[V, V1](f: TransformFunc[V, V1]) -> partial[dict[Any, V1]]:
    return partial(dcz.valmap, f)


def filter_items[K, V](
    predicate: CheckFunc[tuple[K, V]],
) -> Callable[[dict[K, V]], dict[K, V]]:
    return partial(dcz.itemfilter, predicate)


def filter_keys[K](predicate: CheckFunc[K]) -> partial[dict[K, Any]]:
    return partial(dcz.keyfilter, predicate)


def filter_values[V](predicate: CheckFunc[V]) -> partial[dict[Any, V]]:
    return partial(dcz.valfilter, predicate)


def with_key[K, V](key: K, value: V) -> partial[dict[K, V]]:
    return partial(dcz.assoc, key=key, value=value)


def with_nested_key[K, V](keys: Iterable[K] | K, value: V) -> partial[dict[K, V]]:
    return partial(dcz.assoc_in, keys=keys, value=value)


def update_in[K, V](keys: Iterable[K], f: ProcessFunc[V]) -> partial[dict[K, V]]:
    return partial(dcz.update_in, keys=keys, func=f)


def merge[K, V](others: Iterable[dict[K, V]]) -> partial[dict[K, V]]:
    return partial(_merge, others=others)


def merge_with[K, V](f: Callable[[Any], V], *others: dict[K, V]) -> partial[dict[K, V]]:
    return partial(dcz.merge_with, f, *others)


def drop[K](keys: Iterable[K]) -> partial[dict[K, Any]]:
    return partial(_drop, keys=keys)


def flatten_keys():
    return partial(_flatten_recursive)
