import functools as ft
import itertools as it
import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Self

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain


@dataclass(slots=True, frozen=True)
class BaseDictChain[K, V](BaseChain[dict[K, V]]):
    def filter_items(self, predicate: lf.CheckFunc[tuple[K, V]]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.itemfilter, predicate=predicate))

    def filter_keys(self, predicate: lf.CheckFunc[K]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.keyfilter, predicate=predicate))

    def filter_values(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.valfilter, predicate=predicate))

    def with_key(self, key: K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc_in, keys=keys, value=value))

    def update_in(self, *keys: K, f: lf.ProcessFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[K, V]) -> Self:
        return self.do(f=ft.partial(lf.merge, others=others))

    def drop(self, *keys: K) -> Self:
        return self.do(f=ft.partial(lf.dissoc, keys=keys))


@dataclass(slots=True, frozen=True)
class BaseIterChain[V](BaseChain[Iterable[V]]):
    _value: Iterable[V]

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
        self, probability: float, state: lf.RandomProtocol | int | None = None
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
        return self.do(f=ft.partial(cz.itertoolz.accumulate, binop=op.add))

    def cumprod(self) -> Self:
        return self.do(f=ft.partial(cz.itertoolz.accumulate, binop=op.mul))

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        return self.do(f=ft.partial(lf.merge_sorted, others=others, sort_on=sort_on))

    def as_list(self) -> Self:
        return self.do(list)

    def as_tuple(self) -> Self:
        return self.do(tuple)

    def to_list(self) -> list[V]:
        return list(self.to_unwrap())

    def to_tuple(self) -> tuple[V, ...]:
        return tuple(self.to_unwrap())
