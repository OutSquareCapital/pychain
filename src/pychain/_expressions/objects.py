import operator
from collections.abc import Callable, Iterable
from typing import Any


def attr[T](*names: str) -> Callable[[T], T]:
    return operator.attrgetter(*names)  # type: ignore[return-value]


def item[T](*keys: Any) -> Callable[[Iterable[T]], T]:
    return operator.itemgetter(*keys)  # type: ignore[return-value]


def method[P](name: str, *args: P, **kwargs: P) -> Callable[[P], Any]:
    return operator.methodcaller(name, *args, **kwargs)
