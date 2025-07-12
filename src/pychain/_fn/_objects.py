import operator
from collections.abc import Iterable
from typing import Any
import cytoolz as cz

from .._protocols import ThreadFunc

call = operator.call
attr = operator.attrgetter
item = operator.itemgetter
method = operator.methodcaller
compose = cz.functoolz.compose_left


def thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_first(val, *fns)


def thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_last(val, *fns)


def merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    return cz.dicttoolz.merge(on, *others)

def dissoc[K, V](data: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return cz.dicttoolz.dissoc(data, *keys)

def flatten_recursive[V](
    d: dict[Any, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    items: dict[str, V] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items
