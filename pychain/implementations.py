import functools as ft
from collections.abc import Callable
from dataclasses import dataclass

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain
from pychain.dict_base import BaseDictChain
from pychain.iter_base import BaseIterChain


@dataclass(slots=True, frozen=True, repr=False)
class ScalarChain[T](BaseChain[T]):
    def do_as[T1](self, f: lf.TransformFunc[T, T1]) -> "ScalarChain[T1]":
        return ScalarChain(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def to_iter(self, n: int) -> "IterChain[T]":
        return IterChain(_value=iter([self.unwrap()])).repeat(n=n)

    def to_dict(self, n: int) -> "DictChain[int, T]":
        val = self.unwrap()
        return DictChain(_value={i: val for i in range(n)})

    def to_iter_dict[K](self, n: int, *keys: K) -> "DictChain[K, IterChain[T]]":
        val = self.to_iter(n=n)
        return DictChain(_value={k: val for k in keys})


@dataclass(slots=True, frozen=True, repr=False)
class IterChain[V](BaseIterChain[V]):
    def to_scalar[V1](self, f: lf.AggFunc[V, V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self.unwrap()))

    def to_dict(self) -> "DictChain[int, V]":
        return DictChain(_value={i: v for i, v in enumerate(self.unwrap())})

    def to_iter_dict[K](self, n: int) -> "DictChain[int, IterChain[V]]":
        return DictChain(_value={k: self for k in range(n)})

    def to_iter_dict_with_keys[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        return DictChain(_value={k: self for k in keys})

    def to_groups[K](self, on: lf.TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self.unwrap())
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def to_reduced_groups[K](
        self, key: lf.TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.unwrap()))

    def to_frequencies(self) -> "DictChain[V, int]":
        return DictChain(_value=cz.itertoolz.frequencies(self.unwrap()))

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

    def is_all(self) -> bool:
        return all(self.unwrap())

    def is_any(self) -> bool:
        return any(self.unwrap())

    def is_distinct(self) -> bool:
        return cz.itertoolz.isdistinct(self.unwrap())

    def is_iterable(self) -> bool:
        return cz.itertoolz.isiterable(self.unwrap())


@dataclass(slots=True, frozen=True, repr=False)
class DictChain[K, V](BaseDictChain[K, V]):
    def to_scalar_value[V1](self, f: lf.AggFunc[V, V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self.unwrap().values()))

    def to_scalar_key[K1](self, f: lf.AggFunc[K, K1]) -> ScalarChain[K1]:
        return ScalarChain(_value=f(self.unwrap().keys()))

    def to_scalar_items[K1, V1](
        self, f: lf.AggFunc[tuple[K, V], tuple[K1, V1]]
    ) -> ScalarChain[tuple[K1, V1]]:
        return ScalarChain(_value=f(self.unwrap().items()))

    def to_iter_keys(self) -> "IterChain[K]":
        return IterChain(_value=self.unwrap().keys())

    def to_iter_values(self) -> "IterChain[V]":
        return IterChain(_value=self.unwrap().values())

    def to_iter_items(self) -> "IterChain[tuple[K, V]]":
        return IterChain(_value=self.unwrap().items())
