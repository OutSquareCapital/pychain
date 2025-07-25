from collections.abc import Callable, Iterable
from functools import reduce
from itertools import dropwhile, product, takewhile
from random import Random
from typing import TYPE_CHECKING, Any

import cytoolz.itertoolz as itz

from . import consts as fn
from ._exprs import BaseExpr
from ._protocols import get_placeholder, Operation

if TYPE_CHECKING:
    from ._exprs import Expr
    from ._struct import Struct


class Iter[VP, VR](BaseExpr[Iterable[VP], VR]):
    @property
    def _arg(self) -> Iterable[VR]:
        return get_placeholder(Iterable[VR])

    def _do[T, **P](
        self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> "Iter[VP, T]":
        op = Operation(func=func, args=args, kwargs=kwargs)
        return self._new(op)

    def into[T](self, obj: Callable[[Iterable[VR]], T]):
        return self._do(obj, self._arg)

    def map[T](self, f: fn.Transform[VR, T]) -> "Iter[VP, T]":
        return self._do(map, f, self._arg)  # type: ignore

    def filter(self, f: fn.Check[VR]) -> "Iter[VP, VR]":
        return self._do(filter, f, self._arg)  # type: ignore

    def take_while(self, predicate: fn.Check[VR]) -> "Iter[VP, VR]":
        return self._do(takewhile, predicate, self._arg)  # type: ignore

    def drop_while(self, predicate: fn.Check[VR]) -> "Iter[VP, VR]":
        return self._do(dropwhile, predicate, self._arg)  # type: ignore

    def agg[T](self, f: Callable[[Iterable[VR]], T]) -> "Expr[Iterable[VP], T]":
        from ._exprs import Expr

        return Expr(self._do(f, self._arg)._pipeline)

    def group_by[K](self, on: fn.Transform[VR, K]) -> "Struct[VP, K, VR, list[VR]]":
        from ._struct import Struct

        return Struct(self._do(itz.groupby, on, self._arg)._pipeline)

    def into_frequencies(self) -> "Struct[VP, int, VR, int]":
        from ._struct import Struct

        return Struct(self._do(itz.frequencies, self._arg)._pipeline)

    def reduce_by[K](self, key: fn.Transform[VR, K], binop: Callable[[VR, VR], VR]):
        return self._do(itz.reduceby, key, binop, self._arg)

    def flat_map[V1](self, f: fn.Transform[VR, Iterable[V1]]):
        def _flat_map(value: Iterable[VR]):
            return itz.concat(map(f, value))

        return self._do(_flat_map, self._arg)

    def interpose(self, element: VR):
        return self._do(itz.interpose, element, self._arg)

    def top_n(self, n: int, key: Callable[[VR], Any] | None = None):
        return self._do(itz.topk, n, self._arg, key)

    def random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(itz.random_sample, probability, self._arg, state)

    def accumulate(self, f: Callable[[VR, VR], VR]):
        return self._do(itz.accumulate, f, self._arg)

    def reduce(self, f: Callable[[VR, VR], VR]):
        return self._do(reduce, f, self._arg)

    def insert_left(self, value: VR):
        return self._do(itz.cons, value, self._arg)

    def peekn(self, n: int, note: str | None = None):
        return self._do(peekn, self._arg, n, note)

    def peek(self, note: str | None = None):
        return self._do(peek, self._arg, note)

    def head(self, n: int):
        return self._do(itz.take, n, self._arg)

    def tail(self, n: int):
        return self._do(itz.tail, n, self._arg)

    def drop_first(self, n: int):
        return self._do(itz.drop, n, self._arg)

    def every(self, index: int):
        return self._do(itz.take_nth, index, self._arg)

    def repeat(self, n: int):
        return self._do(repeat, self._arg, n)

    def unique(self):
        return self._do(itz.unique, self._arg)

    def tap(self, func: Callable[[VR], None]):
        return self._do(tap, self._arg, func)

    def enumerate(self):
        return self._do(enumerate, self._arg)

    def flatten(self):
        return self._do(itz.concat, self._arg)

    def partition(self, n: int, pad: VR | None = None):
        return self._do(itz.partition, n, self._arg, pad)

    def partition_all(self, n: int):
        return self._do(itz.partition_all, n, self._arg)

    def rolling(self, length: int):
        return self._do(itz.sliding_window, length, self._arg)

    def cross_join[T](self, other: Iterable[T]):
        return self._do(product, self._arg, other)

    def diff(
        self,
        *others: Iterable[VR],
        key: fn.Process[VR] | None = None,
    ):
        return self._do(itz.diff, *(self._arg, *others), ccpdefault=None, key=key)

    def zip_with(self, *others: Iterable[VR], strict: bool = False):
        return self._do(zip, self._arg, *others, strict=strict)

    def merge_sorted(
        self, *others: Iterable[VR], sort_on: Callable[[VR], Any] | None = None
    ):
        return self._do(itz.merge_sorted, self._arg, *others, key=sort_on)

    def interleave(self, *others: Iterable[VR]):
        return self._do(itz.interleave, seqs=[self._arg, *others])

    def concat(self, *others: Iterable[VR]):
        return self._do(itz.concat, self._arg, *others)

    def is_distinct(self):
        return self._do(itz.isdistinct, self._arg)

    def is_all(self):
        return self._do(all, self._arg)

    def is_any(self):
        return self._do(any, self._arg)

    def to_dict(self):
        def _to_dict[V](value: Iterable[V]):
            return dict(enumerate(value))

        return self._do(_to_dict, self._arg)

    def first(self):
        return self.agg(itz.first)

    def second(self):
        return self.agg(itz.second)

    def last(self):
        return self.agg(itz.last)

    def length(self):
        return self.agg(itz.count)

    def at_index(self, index: int):
        def _at_index(value: Iterable[VR]) -> VR:
            return itz.nth(index, value)

        return self.agg(_at_index)


def peekn[T](seq: Iterable[T], n: int, note: str | None = None):
    values, sequence = itz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def peek[T](seq: Iterable[T], note: str | None = None):
    value, sequence = itz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def repeat[V](value: Iterable[V], n: int) -> Iterable[V]:
    def fn(value: V) -> Iterable[V]:
        return [value] * n

    return itz.concat(seqs=map(fn, value))


def tap[V](value: Iterable[V], func: Callable[[V], None]):
    for item in value:
        func(item)
        yield item
