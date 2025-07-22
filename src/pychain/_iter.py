from collections.abc import Callable, Iterable, Iterator
from functools import partial, reduce
from itertools import dropwhile, product, starmap, takewhile
from random import Random
from typing import Any, TYPE_CHECKING

import cytoolz.itertoolz as itz

from . import funcs as fn
from ._exprs import BaseExpr, collect_pipeline
from ._protocols import (
    CheckFunc,
    ProcessFunc,
    TransformFunc,
)

if TYPE_CHECKING:
    from ._exprs import Expr
    from ._struct import Struct


class Iter[VP, VR](BaseExpr[Iterable[VP], Iterable[VR]]):
    def _do[T](self, f: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return Iter(pipeline=self._pipeline + [f])

    def into[T](self, obj: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return self._do(obj)

    def map_compose(self, fns: Iterable[ProcessFunc[VR]]) -> "Iter[VP, VR]":
        mapping_func = collect_pipeline(list(fns))
        return self._do(partial(map, mapping_func))  # type: ignore

    def agg[T](self, f: Callable[[Iterable[VR]], T]) -> "Expr[Iterable[VP], T]":
        from ._exprs import Expr

        return Expr(self._do(f)._pipeline)

    def group_by[K](
        self, on: TransformFunc[VR, K]
    ) -> "Struct[VP, K, VR, Iterable[VR]]":
        from ._struct import Struct

        return Struct(self._do(partial(itz.groupby, on))._pipeline)

    def into_frequencies(self) -> "Struct[VP, int, VR, int]":
        from ._struct import Struct

        return Struct(self._do(itz.frequencies)._pipeline)

    def reduce_by[K](
        self, key: TransformFunc[VR, K], binop: Callable[[VR, VR], VR]
    ) -> "Iter[VP, dict[K, VR]]":
        return self._do(partial(itz.reduceby, key=key, binop=binop))

    def map[T](self, f: TransformFunc[VR, T] | T) -> "Iter[VP, T]":
        return self._do(f=partial(map, f))  # type: ignore

    def filter(self, f: CheckFunc[VR] | bool) -> "Iter[VP, VR]":
        return self._do(f=partial(filter, f))  # type: ignore

    def flat_map[V1](self, f: TransformFunc[VR, Iterable[V1]]):
        def _flat_map(value: Iterable[VR]):
            return itz.concat(map(f, value))

        return self._do(f=partial(_flat_map))

    def starmap(self, f: TransformFunc[VR, VR]):
        return self._do(f=partial(starmap, f))  # type: ignore

    def take_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=partial(takewhile, predicate))  # type: ignore

    def drop_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=partial(dropwhile, predicate))  # type: ignore

    def interpose(self, element: VR):
        return self._do(f=partial(itz.interpose, element))

    def top_n(self, n: int, key: Callable[[VR], Any] | None = None):
        return self._do(f=partial(itz.topk, n, key=key))

    def random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(f=partial(itz.random_sample, probability, random_state=state))

    def accumulate(self, f: Callable[[VR, VR], VR]):
        return self._do(f=partial(itz.accumulate, f))

    def reduce(self, f: Callable[[VR, VR], VR]):
        return self._do(f=partial(reduce, f))

    def insert_left(self, value: VR):
        return self._do(f=partial(itz.cons, value))

    def peekn(self, n: int, note: str | None = None):
        return self._do(f=partial(fn.peekn, n=n, note=note))

    def peek(self, note: str | None = None):
        return self._do(f=partial(fn.peek, note=note))

    def head(self, n: int):
        return self._do(f=partial(itz.take, n))

    def tail(self, n: int):
        return self._do(f=partial(itz.tail, n))

    def drop_first(self, n: int):
        return self._do(f=partial(itz.drop, n))

    def every(self, index: int):
        return self._do(f=partial(itz.take_nth, index))

    def repeat(self, n: int):
        return self._do(f=partial(fn.repeat, n=n))

    def unique(self):
        return self._do(f=itz.unique)

    def tap(self, func: Callable[[VR], None]):
        return self._do(f=partial(fn.tap, func=func))

    def enumerate(self) -> "Iter[VP, enumerate[VR]]":
        return self._do(f=enumerate)

    def flatten(self) -> "Iter[VP, Any]":
        return self._do(f=itz.concat)

    def partition(
        self, n: int, pad: VR | None = None
    ) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=partial(itz.partition, n, pad=pad))

    def partition_all(self, n: int) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=partial(itz.partition_all, n))

    def rolling(self, length: int):
        return self._do(f=partial(itz.sliding_window, length))

    def cross_join(self, other: Iterable[Any]):
        return self._do(partial(product, other))

    def diff(
        self,
        *others: Iterable[VR],
        key: ProcessFunc[VR] | None = None,
    ):
        def _diff[T, V](value: Iterable[T]):
            return itz.diff(*(value, *others), ccpdefault=None, key=key)

        return self._do(f=partial(_diff))

    def zip_with(
        self, *others: Iterable[VR], strict: bool = False
    ) -> "Iter[VP, zip[tuple[Any, ...]]]":
        def _zip_with[T](value: Iterable[T]):
            return zip(value, *others, strict=strict)

        return self._do(f=partial(_zip_with))

    def merge_sorted(
        self, *others: Iterable[VR], sort_on: Callable[[VR], Any] | None = None
    ):
        def _merge_sorted[V](on: Iterable[V]):
            return itz.merge_sorted(on, *others, key=sort_on)

        return self._do(f=partial(_merge_sorted))

    def interleave(self, *others: Iterable[VR]):
        def _interleave(on: Iterable[VR]):
            return itz.interleave(seqs=[on, *others])

        return self._do(f=partial(_interleave))

    def concat(self, *others: Iterable[VR]):
        def _concat[V](on: Iterable[V]):
            return itz.concat([on, *others])

        return self._do(f=partial(_concat))

    def is_distinct(self):
        return self._do(itz.isdistinct)

    def is_all(self):
        return self._do(all)

    def is_any(self):
        return self._do(any)

    def to_dict(self):
        def _to_dict[V](value: Iterable[V]):
            return dict(enumerate(value))

        return self._do(_to_dict)

    def first(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.first)

    def second(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.second)

    def last(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.last)

    def length(self) -> "Expr[Iterable[VP], int]":
        return self.agg(itz.count)

    def at_index(self, index: int):
        return self.agg(partial(itz.nth, index))
