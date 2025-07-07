import functools as ft
from collections.abc import Callable, Iterable
from copy import deepcopy
from dataclasses import dataclass

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain
from pychain.dict_base import BaseDictChain
from pychain.iter_base import BaseIterChain


@dataclass(slots=True, frozen=True)
class ScalarChain[T](BaseChain[T]):
    def transform[T1](self, f: lf.TransformFunc[T, T1]) -> "ScalarChain[T1]":
        return ScalarChain(_value=f(self.to_unwrap()))

    def to_iter(self) -> "IterChain[T]":
        return IterChain(_value=iter([self.to_unwrap()]))

    def to_dict[K](self, *keys: K) -> "DictChain[K, T]":
        return DictChain.from_scalar(value=self.to_unwrap(), keys=keys)

    def to_lazy_dict[K](self, *keys: K) -> "DictChain[K, IterChain[T]]":
        return DictChain.from_scalar(value=self.to_iter(), keys=keys)


@dataclass(slots=True, frozen=True)
class DictChain[K, V](BaseDictChain[K, V]):
    @classmethod
    def from_scalar[K1, V1](cls, value: V1, keys: Iterable[K1]) -> "DictChain[K1, V1]":
        return DictChain(_value={k: deepcopy(value) for k in keys})

    @property
    def agg(self) -> "Aggregator[V]":
        return Aggregator(_value=self.to_unwrap().values())

    def transform[K1, V1](
        self, f: lf.TransformFunc[dict[K, V], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return DictChain(_value=f(self.to_unwrap()))

    def to_keys_iter(self) -> "IterChain[K]":
        return IterChain(_value=self.to_unwrap().keys())

    def to_values_iter(self) -> "IterChain[V]":
        return IterChain(_value=self.to_unwrap().values())


@dataclass(slots=True, frozen=True)
class IterChain[V](BaseIterChain[V]):
    def transform[V1](
        self, f: lf.TransformFunc[Iterable[V], Iterable[V1]]
    ) -> "IterChain[V1]":
        return IterChain(_value=f(self.to_unwrap()))

    @property
    def agg(self) -> "Aggregator[V]":
        return Aggregator(_value=self.to_unwrap())

    def group_by[K](self, on: lf.TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self._value)
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def reduce_by[K](
        self, key: lf.TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.to_unwrap()))

    def to_frequencies(self) -> "DictChain[V, int]":
        return DictChain(_value=cz.itertoolz.frequencies(self.to_unwrap()))

    def to_lazy_dict[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        return DictChain.from_scalar(value=self, keys=keys)


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

    def is_iterable(self) -> ScalarChain[bool]:
        return ScalarChain(_value=cz.itertoolz.isiterable(self._value))
