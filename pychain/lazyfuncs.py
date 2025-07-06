import functools as ft
from collections.abc import Callable, Iterable
from typing import Any, ParamSpec, Protocol, TypeVar

import cytoolz as cz

P = ParamSpec("P")
R = TypeVar("R")


class RandomProtocol(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...


def lazy(*func: Callable[P, R]) -> Callable[P, R]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @ft.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            print(f"Lazy eval of {f.__name__} with args: {args}, kwargs: {kwargs}")
            return f(*args, **kwargs)

        return wrapper

    return decorator(*func)


type CheckFunc[T] = Callable[[T], bool]
type ProcessFunc[T] = Callable[[T], T]
type TransformFunc[T, T1] = Callable[[T], T1]
type ThreadFunc[T] = ProcessFunc[T] | tuple[ProcessFunc[T], Any]


def thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_first(val, *fns)


def thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_last(val, *fns)


def merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    return cz.dicttoolz.merge(*others, on)


def merge_with[K, V, V1](
    f: Callable[..., V1], on: dict[K, V], others: Iterable[dict[K, V]]
) -> dict[K, V1]:
    return cz.dicttoolz.merge_with(f, on, *others)


def dissoc[K, V](d: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return cz.dicttoolz.dissoc(d=d, *keys)
