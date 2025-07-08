import functools as ft
import itertools as it
import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz

from ._lazyfuncs import (
    TransformFunc,
    CheckFunc,
    Random,
    ProcessFunc,
    interleave,
    concat,
    repeat,
    merge_sorted,
    zip_with,
    diff_with,
    flat_map,
    peek,
    peekn,
    tap,
)
from ._core import AbstractChain
from ._executors import Checker, Converter

if TYPE_CHECKING:
    from ._implementations import IterChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseIterChain[V](AbstractChain[Iterable[V]]):
    _value: Iterable[V]

    @property
    def convert_to(self) -> Converter[V]:
        return Converter(_value=self.unwrap())

    @property
    def check_if(self) -> Checker[V]:
        return Checker(_value=self.unwrap())

    def into[V1](self, f: TransformFunc[Iterable[V], Iterable[V1]]) -> "IterChain[V1]":
        return self.__class__(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def in_range(self, n: int):
        return self.flat_map(lambda x: (x for _ in range(n)))

    def take_while(self, predicate: CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(it.takewhile, predicate))

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(it.dropwhile, predicate))

    def interleave(self, *others: Iterable[V]) -> Self:
        return self.do(f=ft.partial(interleave, others=others))

    def interpose(self, element: V) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.interpose, el=element))

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.topk, k=n, key=key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        return self.do(
            f=ft.partial(
                cz.itertoolz.random_sample, prob=probability, random_state=state
            )
        )

    def concat(self, *others: Iterable[V]) -> Self:
        return self.do(f=ft.partial(concat, others=others))

    def filter(self, f: CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(filter, f))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, binop=f))

    def cons(self, value: V) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.cons, el=value))

    def peek(self, note: str | None = None) -> Self:
        return self.do(f=ft.partial(peek, note=note))

    def peekn(self, n: int, note: str | None = None) -> Self:
        return self.do(f=ft.partial(peekn, n=n, note=note))

    def head(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.take, n=n))

    def tail(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.tail, n=n))

    def drop_first(self, n: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.drop, n=n))

    def every(self, index: int) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.take_nth, n=index))

    def repeat(self, n: int) -> Self:
        return self.do(f=ft.partial(repeat, n=n))

    def unique(self) -> Self:
        return self.do(f=cz.itertoolz.unique)

    def cumsum(self) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.add))

    def cumprod(self) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, op.mul))

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        return self.do(f=ft.partial(merge_sorted, others=others, sort_on=sort_on))

    def tap(self, func: Callable[[V], None]) -> Self:
        return self.do(f=ft.partial(tap, func=func))

    def zip(
        self, *others: Iterable[Any], strict: bool = False
    ) -> "IterChain[tuple[V, ...]]":
        return self.into(f=ft.partial(zip_with, others=others, strict=strict))

    def enumerate(self) -> "IterChain[tuple[int, V]]":
        return self.into(f=enumerate)

    def map[V1](self, f: TransformFunc[V, V1]) -> "IterChain[V1]":
        return self.into(f=ft.partial(map, f))

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "IterChain[V1]":
        return self.into(f=ft.partial(flat_map, func=f))

    def flatten(self) -> "IterChain[Any]":
        return self.into(f=cz.itertoolz.concat)

    def diff(
        self,
        *others: Iterable[V],
        key: ProcessFunc[V] | None = None,
    ) -> "IterChain[tuple[V, ...]]":
        return self.into(f=ft.partial(diff_with, others=others, key=key))

    def partition(self, n: int, pad: V | None = None) -> "IterChain[tuple[V, ...]]":
        return self.into(f=ft.partial(cz.itertoolz.partition, n=n, pad=pad))

    def partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        return self.into(f=ft.partial(cz.itertoolz.partition_all, n=n))

    def rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        return self.into(f=ft.partial(cz.itertoolz.sliding_window, length))
