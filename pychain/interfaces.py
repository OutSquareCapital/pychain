import functools as ft
import itertools as it
import operator as op
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, Self
import cytoolz as cz
import functional as fn  # type: ignore
import polars as pl

import pychain.lazyfuncs as lf


@dataclass(slots=True, frozen=True)
class BaseChain[T](ABC):
    _value: T
    _pipeline: list[lf.ProcessFunc[T]] = field(
        default_factory=list[lf.ProcessFunc[T]], init=False
    )

    @lf.lazy
    def do(self, f: lf.ProcessFunc[T]) -> Self:
        self._pipeline.append(f)
        return self

    @abstractmethod
    def transform[T1](self, f: Callable[[T], Any]) -> Any:
        raise NotImplementedError

    @lf.lazy
    def pipe(self, *fns: lf.ProcessFunc[T]) -> Self:
        return self.do(f=(cz.functoolz.compose_left(*fns)))

    @lf.lazy
    def thread_first(self, *fns: lf.ThreadFunc[T]) -> Self:
        return self.do(f=ft.partial(lf.thread_first, fns=fns))

    @lf.lazy
    def thread_last(self, *fns: lf.ThreadFunc[T]) -> Self:
        return self.do(f=ft.partial(lf.thread_last, fns=fns))

    def unwrap(self) -> T:
        return self.collect()._value

    def collect(self) -> Self:
        if not self._pipeline:
            return self
        return self.__class__(_value=cz.functoolz.pipe(self._value, *self._pipeline))

    def to_series(self) -> pl.Series:
        return pl.Series(values=self.unwrap())

    def to_frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.unwrap())

    def to_lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.unwrap())

    def to_functional(self):
        return fn.seq(self._value)


@dataclass(slots=True, frozen=True)
class BaseDictChain[K, V](BaseChain[dict[K, V]]):
    @lf.lazy
    def filter_items(self, predicate: lf.CheckFunc[tuple[K, V]]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.itemfilter, predicate=predicate))

    @lf.lazy
    def filter_keys(self, predicate: lf.CheckFunc[K]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.keyfilter, predicate=predicate))

    @lf.lazy
    def filter_values(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.valfilter, predicate=predicate))

    @lf.lazy
    def with_key(self, key: K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc, key=key, value=value))

    @lf.lazy
    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc_in, keys=keys, value=value))

    @lf.lazy
    def update_in(self, *keys: K, f: lf.ProcessFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.update_in, keys=keys, func=f))

    @lf.lazy
    def merge(self, *others: dict[K, V]) -> Self:
        return self.do(f=ft.partial(lf.merge, others=others))

    @lf.lazy
    def drop(self, *keys: K) -> Self:
        return self.do(f=ft.partial(lf.dissoc, keys=keys))


@dataclass(slots=True, frozen=True)
class BaseIterChain[V]:
    _value: Iterable[V]

    @classmethod
    def _new(cls, value: Iterable[V]) -> Self:
        return cls(value)

    def take_while(self, predicate: lf.CheckFunc[V]) -> Self:
        return self._new(value=it.takewhile(predicate, self._value))

    def drop_while(self, predicate: lf.CheckFunc[V]) -> Self:
        return self._new(value=it.dropwhile(predicate, self._value))

    @lf.lazy
    def interleave(self, *others: Iterable[V]) -> Self:
        return self._new(value=cz.itertoolz.interleave([self._value, *others]))

    @lf.lazy
    def interpose(self, element: V) -> Self:
        return self._new(value=cz.itertoolz.interpose(el=element, seq=self._value))

    @lf.lazy
    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        return self._new(value=cz.itertoolz.topk(k=n, seq=self._value, key=key))

    @lf.lazy
    def random_sample(
        self, probability: float, state: lf.RandomProtocol | int | None = None
    ) -> Self:
        return self._new(
            value=cz.itertoolz.random_sample(
                prob=probability, seq=self._value, random_state=state
            )
        )

    @lf.lazy
    def distinct_by[K](self, key: lf.TransformFunc[V, K]) -> Self:
        def gen() -> Iterable[V]:
            seen: set[K] = set()
            for item in self._value:
                k: K = key(item)
                if k not in seen:
                    seen.add(k)
                    yield item

        return self._new(value=gen())

    @lf.lazy
    def concat(self, *others: Iterable[V]) -> Self:
        return self._new(value=cz.itertoolz.concat([self._value, *others]))

    @lf.lazy
    def filter(self, f: lf.CheckFunc[V]) -> Self:
        return self._new(value=filter(f, self._value))

    @lf.lazy
    def iterate(self, f: lf.ProcessFunc[V], arg: V) -> Self:
        return self._new(value=cz.itertoolz.iterate(func=f, x=arg))

    @lf.lazy
    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        return self._new(value=cz.itertoolz.accumulate(f, self._value))

    @lf.lazy
    def cons(self, value: V) -> Self:
        return self._new(value=cz.itertoolz.cons(value, self._value))

    @lf.lazy
    def peek(self) -> Self:
        val, _ = cz.itertoolz.peek(self._value)
        print(f"Peeked value: {val}")
        return self

    @lf.lazy
    def peekn(self, n: int) -> Self:
        values, _ = cz.itertoolz.peekn(n, self._value)
        print(f"Peeked {n} values: {list(values)}")
        return self

    @lf.lazy
    def head(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.take(n, self._value))

    @lf.lazy
    def tail(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.tail(n, self._value))

    @lf.lazy
    def drop_first(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.drop(n, self._value))

    @lf.lazy
    def every(self, index: int) -> Self:
        return self._new(value=cz.itertoolz.take_nth(index, self._value))

    @lf.lazy
    def repeat(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.concat(map(lambda x: [x] * n, self._value)))

    @lf.lazy
    def unique(self) -> Self:
        return self._new(value=cz.itertoolz.unique(self._value))

    @lf.lazy
    def cumsum(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.add, self._value))

    @lf.lazy
    def cumprod(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.mul, self._value))

    @lf.lazy
    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        return self._new(
            value=cz.itertoolz.merge_sorted(self._value, *others, key=sort_on)
        )

    def to_list(self) -> list[V]:
        return list(self._value)

    def to_tuple(self) -> tuple[V, ...]:
        return tuple(self._value)
