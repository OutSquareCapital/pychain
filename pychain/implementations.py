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
    def apply[T1](self, f: lf.TransformFunc[T, T1]) -> "ScalarChain[T1]":
        return ScalarChain(_value=f(self.to_unwrap()))

    def to_iter(self) -> "IterChain[T]":
        return IterChain.from_scalar(value=self.to_unwrap())

    def to_dict[K](self, *keys: K) -> "DictChain[K, T]":
        return DictChain.from_scalar(value=self.to_unwrap(), keys=keys)

    def to_lazy_dict[K](self, *keys: K) -> "DictChain[K, IterChain[T]]":
        return DictChain.from_scalar(value=self.to_iter(), keys=keys)


@dataclass(slots=True, frozen=True)
class DictChain[K, V](BaseDictChain[K, V]):
    @classmethod
    def from_scalar[K1, V1](cls, value: V1, keys: Iterable[K1]) -> "DictChain[K1, V1]":
        return DictChain(_value={k: deepcopy(value) for k in keys})

    @classmethod
    def from_dict_of_iterables[K1, V1](
        cls, value: dict[K1, Iterable[V1]]
    ) -> "DictChain[K1, IterChain[V1]]":
        return DictChain(_value={k: IterChain(_value=v) for k, v in value.items()})

    def apply[K1, V1](
        self, f: lf.TransformFunc[dict[K, V], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return DictChain(_value=f(self.to_unwrap()))

    def to_keys_iter(self) -> "IterChain[K]":
        return IterChain(_value=self.to_unwrap().keys())

    def to_values_iter(self) -> "IterChain[V]":
        return IterChain(_value=self.to_unwrap().values())


@dataclass(slots=True, frozen=True)
class IterChain[V](BaseIterChain[V]):
    @classmethod
    def from_scalar[T](cls, value: T) -> "IterChain[T]":
        return IterChain(_value=iter([value]))

    @classmethod
    def from_func[T, T1](cls, value: T, f: Callable[[T], T1]) -> "IterChain[T1]":
        return IterChain(_value=cz.itertoolz.iterate(func=f, x=value))

    @classmethod
    def from_range(cls, start: int, stop: int, step: int = 1) -> "IterChain[int]":
        return IterChain(_value=range(start, stop, step))

    def to_dict[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        return DictChain.from_scalar(value=self, keys=keys)

    def to_scalar[V1](self, f: lf.TransformFunc[Iterable[V], V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self.to_unwrap()))

    def apply[V1](
        self, f: lf.TransformFunc[Iterable[V], Iterable[V1]]
    ) -> "IterChain[V1]":
        return IterChain(_value=f(self.to_unwrap()))

    def to_groups[K](self, on: lf.TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self._value)
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def to_reduced_groups[K](
        self, key: lf.TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.to_unwrap()))

    def to_frequencies(self) -> "DictChain[V, int]":
        return DictChain(_value=cz.itertoolz.frequencies(self.to_unwrap()))

    def to_value_first(self) -> ScalarChain[V]:
        return self.to_scalar(f=cz.itertoolz.first)

    def to_value_second(self) -> ScalarChain[V]:
        return self.to_scalar(f=cz.itertoolz.second)

    def to_value_last(self) -> ScalarChain[V]:
        return self.to_scalar(f=cz.itertoolz.last)

    def to_value_at(self, index: int) -> ScalarChain[V]:
        return self.to_scalar(f=ft.partial(cz.itertoolz.nth, n=index))

    def to_len(self) -> ScalarChain[int]:
        return self.to_scalar(f=cz.itertoolz.count)

    def to_sum(self) -> ScalarChain[V]:
        return self.to_scalar(f=sum)  # type: ignore

    def to_min(self) -> ScalarChain[V]:
        return self.to_scalar(f=min)  # type: ignore

    def to_max(self) -> ScalarChain[V]:
        return self.to_scalar(f=max)  # type: ignore

    def is_all(self, predicate: lf.CheckFunc[V]) -> bool:
        return all(self.to_unwrap())

    def is_any(self, predicate: lf.CheckFunc[V]) -> bool:
        return any(self.to_unwrap())

    def is_distinct(self) -> bool:
        return cz.itertoolz.isdistinct(self.to_unwrap())

    def is_iterable(self) -> bool:
        return cz.itertoolz.isiterable(self.to_unwrap())
