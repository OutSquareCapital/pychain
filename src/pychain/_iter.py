from itertools import product, starmap, takewhile, dropwhile
from collections.abc import Callable, Iterable, Iterator
from random import Random
from typing import Any, TYPE_CHECKING

import cytoolz.itertoolz as itz
import functools as ft
from ._protocols import CheckFunc, ProcessFunc, TransformFunc
from ._core import BaseExpr, collect_pipeline

if TYPE_CHECKING:
    from ._exprs import Expr
    from ._structs import Struct


class Iter[VP, VR](BaseExpr[Iterable[VP], VR]):
    __slots__ = "_pipeline"
    def _do[T](self, f: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return Iter(self._pipeline + [f])

    def map_compose(self, fns: Iterable[ProcessFunc[VR]]) -> "Iter[VP, VR]":
        mapping_func = collect_pipeline(list(fns))
        return self._do(ft.partial(map, mapping_func))  # type: ignore

    def into[T](self, obj: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return self._do(obj)

    def agg[T](self, f: Callable[[Iterable[VR]], T]) -> "Expr[Iterable[VP], T]":
        return Expr([self._do(f).collect()])

    def is_distinct(self):
        return self._do(itz.isdistinct)

    def is_all(self):
        return self._do(all)

    def is_any(self):
        return self._do(any)

    def to_dict(self):
        return self._do(iter_to_dict)

    def group_by[K](
        self, on: TransformFunc[VR, K]
    ) -> "Struct[VP, K, VR, Iterable[VR]]":
        return Struct([self._do(ft.partial(itz.groupby, on)).collect().extract()])

    def into_frequencies(self) -> "Struct[VP, int, VR, int]":
        return Struct([self._do(itz.frequencies).collect().extract()])

    def reduce_by[K](
        self, key: TransformFunc[VR, K], binop: Callable[[VR, VR], VR]
    ) -> "Iter[VP, dict[K, VR]]":
        return self._do(ft.partial(itz.reduceby, key=key, binop=binop))

    def map[T](self, f: TransformFunc[VR, T]) -> "Iter[VP, T]":
        return self._do(f=ft.partial(map, f))  # type: ignore

    def filter(self, f: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=ft.partial(filter, f))  # type: ignore

    def flat_map(self, f: TransformFunc[VR, Iterable[VR]]):
        return self._do(f=ft.partial(_flat_map, func=f))

    def starmap(self, f: TransformFunc[VR, VR]):
        return self._do(f=ft.partial(starmap, f))  # type: ignore

    def take_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=ft.partial(takewhile, predicate))  # type: ignore

    def drop_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=ft.partial(dropwhile, predicate))  # type: ignore

    def interpose(self, element: VR):
        return self._do(f=ft.partial(itz.interpose, element))

    def top_n(self, n: int, key: Callable[[VR], Any] | None = None):
        return self._do(f=ft.partial(itz.topk, n, key=key))

    def random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(
            f=ft.partial(itz.random_sample, probability, random_state=state)
        )

    def accumulate(self, f: Callable[[VR, VR], VR]):
        return self._do(f=ft.partial(itz.accumulate, f))

    def reduce[V](self, f: Callable[[VR, VR], VR]):
        return self._do(f=ft.partial(ft.reduce, f))

    def insert_left(self, value: VR):
        return self._do(f=ft.partial(itz.cons, value))

    def peekn(self, n: int, note: str | None = None):
        return self._do(f=ft.partial(_peekn, n=n, note=note))

    def peek(self, note: str | None = None):
        return self._do(f=ft.partial(_peek, note=note))

    def head(self, n: int):
        return self._do(f=ft.partial(itz.take, n))

    def tail(self, n: int):
        return self._do(f=ft.partial(itz.tail, n))

    def drop_first(self, n: int):
        return self._do(f=ft.partial(itz.drop, n))

    def every(self, index: int):
        return self._do(f=ft.partial(itz.take_nth, index))

    def repeat(self, n: int):
        return self._do(f=ft.partial(_repeat, n=n))

    def unique(self):
        return self._do(f=itz.unique)

    def tap(self, func: Callable[[VR], None]):
        return self._do(f=ft.partial(_tap, func=func))

    def enumerate(self) -> "Iter[VP, enumerate[VR]]":
        return self._do(f=enumerate)

    def flatten(self) -> "Iter[VP, Any]":
        return self._do(f=itz.concat)

    def partition(
        self, n: int, pad: VR | None = None
    ) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=ft.partial(itz.partition, n, pad=pad))

    def partition_all(self, n: int) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=ft.partial(itz.partition_all, n))

    def rolling(self, length: int):
        return self._do(f=ft.partial(itz.sliding_window, length))

    def cross_join(self, other: Iterable[Any]):
        return self._do(ft.partial(product, other))

    def diff(
        self,
        others: Iterable[Iterable[VR]],
        default: Any | None = None,
        key: ProcessFunc[VR] | None = None,
    ):
        return self._do(f=ft.partial(_diff, others=others, key=key))

    def zip_with(
        self, others: Iterable[Iterable[VR]], strict: bool = False
    ) -> "Iter[VP, zip[tuple[Any, ...]]]":
        return self._do(f=ft.partial(_zip_with, others=others, strict=strict))

    def merge_sorted(
        self, others: Iterable[Iterable[VR]], sort_on: Callable[[VR], Any] | None = None
    ):
        return self._do(f=ft.partial(_merge_sorted, others=others, sort_on=sort_on))

    def interleave(self, *others: Iterable[VR]):
        return self._do(f=ft.partial(_interleave, others=others))

    def concat(self, *others: Iterable[VR]):
        return self._do(f=ft.partial(_concat, others=others))

    def first(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.first)

    def second(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.second)

    def last(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.last)

    def length(self) -> "Expr[Iterable[VP], int]":
        return self.agg(itz.count)

    def at_index(self, index: int):
        return self.agg(ft.partial(itz.nth, index))


def _merge_sorted[V](
    on: Iterable[V],
    others: Iterable[Iterable[V]],
    sort_on: Callable[[V], Any] | None = None,
):
    return itz.merge_sorted(on, *others, key=sort_on)


def _concat[V](on: Iterable[V], others: Iterable[Iterable[V]]):
    return itz.concat([on, *others])


def _flat_map[V, V1](value: Iterable[V], func: TransformFunc[V, Iterable[V1]]):
    return itz.concat(map(func, value))


def _peekn(seq: Iterable[Any], n: int, note: str | None = None):
    values, sequence = itz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def _peek[T](seq: Iterable[T], note: str | None = None):
    value, sequence = itz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def _repeat[V](value: Iterable[V], n: int) -> Iterable[V]:
    def fn(value: V) -> Iterable[V]:
        return [value] * n

    return itz.concat(seqs=map(fn, value))


def _diff[T, V](
    value: Iterable[T],
    others: Iterable[Iterable[T]],
    ccpdefault: Any | None = None,
    key: ProcessFunc[V] | None = None,
):
    return itz.diff(*(value, *others), ccpdefault=ccpdefault, key=key)


def _zip_with[T](value: Iterable[T], others: Iterable[Iterable[Any]], strict: bool):
    return zip(value, *others, strict=strict)


def _interleave[V](on: Iterable[V], others: Iterable[Iterable[V]]):
    return itz.interleave(seqs=[on, *others])


def iter_to_dict[V](value: Iterable[V]):
    return dict(enumerate(value))


def _tap[V](value: Iterable[V], func: Callable[[V], None]):
    for item in value:
        func(item)
        yield item
