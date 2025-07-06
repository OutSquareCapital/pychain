import functools as ft
from collections.abc import Callable, Iterable, Iterator
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
            # print(f"Lazy eval of {f.__name__}\n with args: \n{args}, kwargs: \n{kwargs}")
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


def map_items[K, V, K1, V1](
    d: dict[K, V], func: TransformFunc[tuple[K, V], tuple[K1, V1]]
) -> dict[K1, V1]:
    return cz.dicttoolz.itemmap(d=d, func=func)


def map_keys[K, V, K1](d: dict[K, V], func: TransformFunc[K, K1]) -> dict[K1, V]:
    return cz.dicttoolz.keymap(d=d, func=func)


def map_values[K, V, V1](d: dict[K, V], func: TransformFunc[V, V1]) -> dict[K, V1]:
    return cz.dicttoolz.valmap(d=d, func=func)


def repeat[V](value: Iterable[V], n: int) -> Iterator[V]:
    return cz.itertoolz.concat(seqs=map(lambda x: [x] * n, value))


def concat[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    return cz.itertoolz.concat([on, *others])


def interleave[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    return cz.itertoolz.interleave(seqs=[on, *others])


def merge_sorted[V](
    on: Iterable[V],
    others: Iterable[Iterable[V]],
    sort_on: Callable[[V], Any] | None = None,
) -> Iterator[V]:
    return cz.itertoolz.merge_sorted(on, *others, key=sort_on)


def peek[T](seq: Iterable[T], note: str | None = None) -> Iterable[T]:
    value, sequence = cz.itertoolz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def peekn[T](seq: Iterable[T], n: int, note: str | None = None) -> Iterable[T]:
    values, sequence = cz.itertoolz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def flat_map[V, V1](
    value: Iterable[V], func: TransformFunc[V, Iterable[V1]]
) -> Iterable[V1]:
    return cz.itertoolz.concat(map(func, value))


def diff_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[T]], key: ProcessFunc[V] | None = None
) -> Iterable[tuple[T, ...]]:
    return cz.itertoolz.diff(value, *others, key=key)


def zip_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[V]], strict: bool
) -> Iterable[tuple[T, V]]:
    return zip(value, *others, strict=strict)
