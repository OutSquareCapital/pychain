import operator
from collections.abc import Callable, Iterable
from typing import Any

import cytoolz as cz

from .._protocols import ThreadFunc


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
