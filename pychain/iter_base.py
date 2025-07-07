import functools as ft
import itertools as it
import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain

if TYPE_CHECKING:
    from pychain.implementations import IterChain


@dataclass(slots=True, frozen=True)
class BaseIterChain[V](BaseChain[Iterable[V]]):
    _value: Iterable[V]

    def transform[V1](
        self, f: Callable[[Iterable[V]], Iterable[V1]]
    ) -> "IterChain[V1]":
        raise NotImplementedError

    def take_while(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(it.takewhile, predicate))

    def drop_while(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(it.dropwhile, predicate))

    def interleave(self, *others: Iterable[V]) -> Self:
        return self.do(f=ft.partial(lf.interleave, others=others))

    def interpose(self, element: V) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.interpose, el=element))

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.topk, k=n, key=key))

    def random_sample(
        self, probability: float, state: lf.Random | int | None = None
    ) -> Self:
        return self.do(
            f=ft.partial(
                cz.itertoolz.random_sample, prob=probability, random_state=state
            )
        )

    def concat(self, *others: Iterable[V]) -> Self:
        return self.do(f=ft.partial(lf.concat, others=others))

    def filter(self, f: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(filter, f))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, binop=f))

    def cons(self, value: V) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.cons, el=value))

    def peek(self, note: str | None = None) -> Self:
        return self.do(f=ft.partial(lf.peek, note=note))

    def peekn(self, n: int, note: str | None = None) -> Self:
        return self.do(f=ft.partial(lf.peekn, n=n, note=note))

    def head(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.take, n=n))

    def tail(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.tail, n=n))

    def drop_first(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.drop, n=n))

    def every(self, index: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.take_nth, n=index))

    def repeat(self, n: int) -> Self:
        return self.do(f=ft.partial(lf.repeat, n=n))

    def unique(self) -> Self:
        return self.do(f=cz.itertoolz.unique)

    def cumsum(self) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.add))

    def cumprod(self) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.mul))

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        return self.do(f=ft.partial(lf.merge_sorted, others=others, sort_on=sort_on))

    def with_for_each[V1](self, f: lf.TransformFunc[V, V1]) -> "IterChain[V1]":
        return self.transform(f=ft.partial(lf.for_each, f=f))

    def with_zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> "IterChain[tuple[V, ...]]":
        return self.transform(f=ft.partial(lf.zip_with, others=others, strict=strict))

    def with_enumerate(self) -> "IterChain[tuple[int, V]]":
        return self.transform(f=enumerate)

    def with_map[V1](self, f: lf.TransformFunc[V, V1]) -> "IterChain[V1]":
        return self.transform(f=ft.partial(map, f))

    def with_flat_map[V1](
        self, f: lf.TransformFunc[V, Iterable[V1]]
    ) -> "IterChain[V1]":
        return self.transform(f=ft.partial(lf.flat_map, func=f))

    def with_flatten(self) -> "IterChain[Any]":
        return self.transform(f=cz.itertoolz.concat)

    def with_diff(
        self,
        *others: Iterable[V],
        key: lf.ProcessFunc[V] | None = None,
    ) -> "IterChain[tuple[V, ...]]":
        return self.transform(f=ft.partial(lf.diff_with, others=others, key=key))

    def with_partition(
        self, n: int, pad: V | None = None
    ) -> "IterChain[tuple[V, ...]]":
        return self.transform(f=ft.partial(cz.itertoolz.partition, n=n, pad=pad))

    def with_partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        return self.transform(f=ft.partial(cz.itertoolz.partition_all, n=n))

    def with_rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        return self.transform(f=ft.partial(cz.itertoolz.sliding_window, length))

    def to_list(self) -> list[V]:
        return list(self.to_unwrap())

    def to_tuple(self) -> tuple[V, ...]:
        return tuple(self.to_unwrap())
