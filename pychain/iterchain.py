import functools as ft
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.interfaces import BaseChain, BaseDictChain, BaseIterChain


@dataclass(slots=True, frozen=True)
class ScalarChain[T](BaseChain[T]):
    def transform[T1](self, f: lf.TransformFunc[T, T1]) -> "ScalarChain[T1]":
        return ScalarChain(_value=f(self.unwrap()))

    def to_iter(self) -> "IterChain[T]":
        return IterChain(_value=iter([self.unwrap()]))

    def to_dict[K](self, *keys: K) -> "DictChain[K, T]":
        val: T = self.unwrap()
        return DictChain(_value={k: val for k in keys})

    def to_lazy_dict[K](self, *keys: K) -> "DictChain[K, IterChain[T]]":
        val: IterChain[T] = self.to_iter()
        return DictChain(_value={k: val for k in keys})


@dataclass(slots=True, frozen=True)
class DictChain[K, V](BaseDictChain[K, V]):
    def transform[K1, V1](
        self, f: lf.TransformFunc[dict[K, V], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return DictChain(_value=f(self.unwrap()))

    def to_keys_iter(self) -> "IterChain[K]":
        return IterChain(_value=self.unwrap().keys())

    def to_values_iter(self) -> "IterChain[V]":
        return IterChain(_value=self.unwrap().values())

    def map_items[K1, V1](
        self, f: lf.TransformFunc[tuple[K, V], tuple[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return self.transform(f=ft.partial(cz.dicttoolz.itemmap, func=f))

    def map_keys[K1](self, f: lf.TransformFunc[K, K1]) -> "DictChain[K1, V]":
        return self.transform(f=ft.partial(cz.dicttoolz.keymap, func=f))

    def map_values[V1](self, f: lf.TransformFunc[V, V1]) -> "DictChain[K, V1]":
        return self.transform(f=ft.partial(cz.dicttoolz.valmap, func=f))

    def merge_with[V1](
        self, f: Callable[..., V1], *others: dict[K, V]
    ) -> "DictChain[K, V1]":
        return self.transform(f=ft.partial(lf.merge_with, f=f, others=others))


@dataclass(slots=True, frozen=True)
class IterChain[V](BaseIterChain[V]):
    def for_each[V1](self, f: lf.TransformFunc[V, V1]) -> "IterChain[V1]":
        new_data: list[V1] = []
        for item in self._value:
            new_data.append(f(item))
        return IterChain(_value=new_data)

    @property
    def agg(self) -> "Aggregator[V]":
        return Aggregator(_value=self._value)

    def range(self, start: int = 0, stop: int = 1, step: int = 1) -> "IterChain[int]":
        return IterChain(_value=range(start, stop, step))

    @lf.lazy
    def zip[V1](
        self, *others: Iterable[V1], strict: bool = False
    ) -> "IterChain[tuple[V, V1]]":
        return IterChain(_value=zip(self._value, *others, strict=strict))

    @lf.lazy
    def enumerate(self) -> "IterChain[tuple[int, V]]":
        return IterChain(_value=enumerate(iterable=self._value))

    @lf.lazy
    def map[V1](self, f: lf.TransformFunc[V, V1]) -> "IterChain[V1]":
        return IterChain(_value=map(f, self._value))

    @lf.lazy
    def flat_map[V1](self, f: lf.TransformFunc[V, Iterable[V1]]) -> "IterChain[V1]":
        return IterChain(_value=cz.itertoolz.concat(map(f, self._value)))

    @lf.lazy
    def flatten(self) -> "IterChain[Any]":
        return IterChain(_value=cz.itertoolz.concat(self._value))

    @lf.lazy
    def diff(
        self, *seqs: Iterable[V], key: lf.ProcessFunc[V] | None = None
    ) -> "IterChain[tuple[V, ...]]":
        return IterChain(_value=cz.itertoolz.diff(self._value, *seqs, key=key))

    def partition(self, n: int, pad: V | None = None) -> "IterChain[tuple[V, ...]]":
        return IterChain(_value=cz.itertoolz.partition(n=n, seq=self._value, pad=pad))

    def partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        return IterChain(_value=cz.itertoolz.partition_all(n=n, seq=self._value))

    def rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        return IterChain(_value=cz.itertoolz.sliding_window(n=length, seq=self._value))

    def group_by[K](self, on: lf.TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self._value)
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def reduce_by[K](
        self, key: lf.TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self._value))

    def frequencies(self) -> "DictChain[V, int]":
        return DictChain(_value=cz.itertoolz.frequencies(self._value))

    def to_lazy_dict[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        return DictChain(_value={k: self for k in keys})


@dataclass(slots=True, frozen=True)
class Aggregator[V]:
    _value: Iterable[V]

    def _to_scalar[V1](self, f: lf.TransformFunc[Iterable[V], V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self._value))

    def _to_numeric[V1: int | float](
        self, f: lf.TransformFunc[Iterable[V], V1]
    ) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self._value))

    def len(self) -> ScalarChain[int]:
        return self._to_numeric(f=cz.itertoolz.count)

    def first(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.first)

    def second(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.second)

    def last(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.last)

    def at(self, index: int) -> ScalarChain[V]:
        return self._to_scalar(f=ft.partial(cz.itertoolz.nth, n=index))

    def sum(self) -> ScalarChain[V]:  # type: ignore
        return self._to_numeric(f=sum)  # type: ignore

    def min(self) -> ScalarChain[V]:  # type: ignore
        return self._to_numeric(f=min)  # type: ignore

    def max(self) -> ScalarChain[V]:  # type: ignore
        return self._to_numeric(f=max)  # type: ignore

    def all(self, predicate: lf.CheckFunc[V]) -> ScalarChain[bool]:
        return ScalarChain(_value=all(map(predicate, self._value)))

    def any(self, predicate: lf.CheckFunc[V]) -> ScalarChain[bool]:
        return ScalarChain(_value=any(map(predicate, self._value)))

    def is_distinct(self) -> ScalarChain[bool]:
        return ScalarChain(_value=cz.itertoolz.isdistinct(seq=self._value))
