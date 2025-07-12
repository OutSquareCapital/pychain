import itertools as it
import operator as op
from collections.abc import Callable, Generator, Iterable, Iterator
from functools import partial
from random import Random
from typing import Any

import cytoolz.itertoolz as itz

from .._protocols import CheckFunc, ProcessFunc, TransformFunc

unique = itz.unique
flatten = itz.concat


def partial_map[V, V1](f: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(map, f)


def partial_filter[V](f: CheckFunc[V]):
    return partial(filter, f)


def zip_with[V](
    others: Iterable[Iterable[V]], strict: bool = False
) -> partial[Iterable[tuple[Any, Any]]]:
    return partial(_zip_with, others=others, strict=strict)


def flat_map[V, V1](f: TransformFunc[V, Iterable[V1]]) -> partial[Iterator[V1]]:
    return partial(_flat_map, func=f)


def merge_sorted[V](
    others: Iterable[Iterable[V]], sort_on: Callable[[V], Any] | None = None
) -> partial[Iterator[V]]:
    return partial(_merge_sorted, others=others, sort_on=sort_on)


def diff[V](
    others: Iterable[Iterable[V]],
    default: Any | None = None,
    key: ProcessFunc[V] | None = None,
) -> partial[Iterable[tuple[V, ...]]]:
    return partial(_diff, others=others, default=default, key=key)


def _repeat[V](value: Iterable[V], n: int) -> Iterator[V]:
    return itz.concat(seqs=map(lambda x: [x] * n, value))


def peek(note: str | None = None):
    return partial(_peek, note=note)


def peekn(n: int, note: str | None = None):
    return partial(_peekn, n=n, note=note)


def starmap[V, V1](f: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(it.starmap, f)

def take_while[V](predicate: CheckFunc[V]):
    return partial(it.takewhile, predicate)


def drop_while[V](predicate: CheckFunc[V]):
    return partial(it.dropwhile, predicate)


def interleave[V](others: Iterable[Iterable[V]]) -> partial[Iterator[V]]:
    return partial(_interleave, others=others)


def interpose[V](element: V) -> partial[Iterator[V]]:
    return partial(itz.interpose, element)


def top_n[V](n: int, key: Callable[[V], Any] | None = None) -> partial[tuple[V, ...]]:
    return partial(itz.topk, n, key=key)


def random_sample(probability: float, state: Random | int | None = None):
    return partial(itz.random_sample, probability, random_state=state)


def concat[V](others: Iterable[Iterable[V]]) -> partial[Iterator[V]]:
    return partial(_concat, others=others)


def accumulate[V](f: Callable[[V, V], V]) -> partial[Iterator[V]]:
    return partial(itz.accumulate, f)


def insert_left[V](value: V) -> partial[Iterator[V]]:
    return partial(itz.cons, value)


def head(n: int):
    return partial(itz.take, n)


def tail(n: int):
    return partial(itz.tail, n)


def drop_first(n: int):
    return partial(itz.drop, n)


def every(index: int):
    return partial(itz.take_nth, index)


def repeat(n: int):
    return partial(_repeat, n=n)


def cumsum():
    return partial(itz.accumulate, op.add)


def cumprod():
    return partial(itz.accumulate, op.mul)


def tap[V](func: Callable[[V], None]) -> partial[Generator[Any, Any, None]]:
    return partial(_tap, func=func)


def partition[V](n: int, pad: V | None = None) -> partial[Iterator[tuple[V, ...]]]:
    return partial(itz.partition, n, pad=pad)


def partition_all(n: int):
    return partial(itz.partition_all, n)


def rolling(length: int):
    return partial(itz.sliding_window, length)


def cross_join[V](other: Iterable[V]) -> partial[Iterator[tuple[V, Any]]]:
    return partial(it.product, other)


def transpose[V]() -> Callable[[Iterable[Iterable[V]]], Iterator[tuple[V, ...]]]:
    return _transpose


def to_records(keys: list[str]):
    return partial_map(lambda row: dict(zip(keys, row))) # type: ignore


def _peek[T](seq: Iterable[T], note: str | None = None) -> Iterator[T]:
    value, sequence = itz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def _peekn[T](seq: Iterable[T], n: int, note: str | None = None) -> Iterator[T]:
    values, sequence = itz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def _tap[V](value: Iterable[V], func: Callable[[V], None]):
    for item in value:
        func(item)
        yield item


def _diff[T, V](
    value: Iterable[T],
    others: Iterable[Iterable[T]],
    default: Any | None = None,
    key: ProcessFunc[V] | None = None,
) -> Iterable[tuple[T, ...]]:
    return itz.diff(*(value, *others), default=default, key=key)


def _flat_map[V, V1](
    value: Iterable[V], func: TransformFunc[V, Iterable[V1]]
) -> Iterator[V1]:
    return itz.concat(map(func, value))


def _zip_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[V]], strict: bool
) -> Iterable[tuple[T, V]]:
    return zip(value, *others, strict=strict)


def _concat[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    return itz.concat([on, *others])


def _interleave[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    return itz.interleave(seqs=[on, *others])


def _merge_sorted[V](
    on: Iterable[V],
    others: Iterable[Iterable[V]],
    sort_on: Callable[[V], Any] | None = None,
) -> Iterator[V]:
    return itz.merge_sorted(on, *others, key=sort_on)


def _transpose[V](iterable: Iterable[Iterable[V]]) -> Iterator[tuple[V, ...]]:
    return zip(*iterable)
