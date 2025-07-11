import operator
from collections.abc import Callable, Iterable
from typing import Any

import cytoolz as cz

from .._protocols import ThreadFunc, ProcessFunc


def attr[T](*names: str) -> Callable[[T], T]:
    return operator.attrgetter(*names)  # type: ignore[return-value]


def item[T](*keys: Any) -> Callable[[Iterable[T]], T]:
    return operator.itemgetter(*keys)  # type: ignore[return-value]


def method[P](name: str, *args: P, **kwargs: P) -> Callable[[P], Any]:
    return operator.methodcaller(name, *args, **kwargs)


def thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_first(val, *fns)


def thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_last(val, *fns)


def merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    return cz.dicttoolz.merge(on, *others)


def dissoc[K, V](d: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return cz.dicttoolz.dissoc(d, *keys)


def compose[T1](*fns: ProcessFunc[T1]):
    return cz.functoolz.compose_left(*fns)


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
