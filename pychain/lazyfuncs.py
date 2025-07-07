from collections.abc import Callable, Iterable, Iterator
from typing import Any, Protocol

import cytoolz as cz


class Random(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...


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


def merge_with[K, V](
    f: Callable[..., V], on: dict[K, V], others: Iterable[dict[K, V]]
) -> dict[K, V]:
    return cz.dicttoolz.merge_with(f, on, *others)


def dissoc[K, V](d: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return cz.dicttoolz.dissoc(d=d, *keys)


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


def for_each[T, T1](value: Iterable[T], f: TransformFunc[T, T1]) -> list[T1]:
    new_data: list[T1] = []
    for item in value:
        new_data.append(f(item))
    return new_data
