from collections.abc import Callable, Iterable, Iterator
from typing import Any, Protocol

import cytoolz as cz


class Random(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...


type CheckFunc[T] = Callable[[T], bool]
type ProcessFunc[T] = Callable[[T], T]
type TransformFunc[T, T1] = Callable[[T], T1]
type AggFunc[V, V1] = Callable[[Iterable[V]], V1]
type ThreadFunc[T] = Callable[..., T] | tuple[Callable[..., T], Any]


def thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_first(val, *fns)


def thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_last(val, *fns)


def merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    return cz.dicttoolz.merge(on, *others)

def dissoc[K, V](d: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    return cz.dicttoolz.dissoc(d, *keys)


def repeat[V](value: Iterable[V], n: int) -> Iterator[V]:
    """
    Repeat each element in the iterable n times (see cytoolz.repeat, cytoolz.concat).

    Example:
        >>> list(repeat([1, 2], 2))
        [1, 1, 2, 2]
    """
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


def peek[T](seq: Iterable[T], note: str | None = None) -> Iterator[T]:
    """
    Peek at the first element of an iterable, printing it, and return the full sequence (see cytoolz.peek).

    Example:
        >>> it = peek([1, 2, 3], note="demo")
        Peeked value (demo): 1
        >>> list(it)
        [1, 2, 3]
    """
    value, sequence = cz.itertoolz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def peekn[T](seq: Iterable[T], n: int, note: str | None = None) -> Iterator[T]:
    """
    Peek at the first n elements of an iterable, printing them, and return the full sequence (see cytoolz.peekn).

    Example:
        >>> it = peekn([1, 2, 3, 4], 2)
        Peeked 2 values: [1, 2]
        >>> list(it)
        [1, 2, 3, 4]
    """
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
    value: Iterable[T],
    others: Iterable[Iterable[T]],
    default: Any | None = None,
    key: ProcessFunc[V] | None = None,
) -> Iterable[tuple[T, ...]]:
    return cz.itertoolz.diff(*(value, *others), default=default, key=key)


def zip_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[V]], strict: bool
) -> Iterable[tuple[T, V]]:
    """
    Zip several iterables together (like built-in zip).

    Example:
        >>> list(zip_with([1, 2], [[10, 20]], strict=False))
        [(1, 10), (2, 20)]
    """
    return zip(value, *others, strict=strict)


def tap[V](value: Iterable[V], func: Callable[[V], Any]) -> Iterator[V]:
    """
    Apply a side-effect function to each element, yielding the original elements (see cytoolz.do/tap).

    Example:
        >>> list(tap([1, 2], print))
        1
        2
        [1, 2]
    """
    for item in value:
        func(item)
        yield item
