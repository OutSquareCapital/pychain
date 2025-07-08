from collections.abc import Callable, Iterable
from dataclasses import dataclass

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain
from pychain.dict_base import BaseDictChain
from pychain.iter_base import BaseIterChain
from pychain.executors import GetterBase


@dataclass(slots=True, frozen=True)
class Getter[V](GetterBase[V]):
    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> "ScalarChain[V1]":
        return ScalarChain(_value=f(self._value))


@dataclass(slots=True, frozen=True, repr=False)
class ScalarChain[T](BaseChain[T]):
    def into[T1](self, f: lf.TransformFunc[T, T1]) -> "ScalarChain[T1]":
        return ScalarChain(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def into_iter(self, n: int) -> "IterChain[T]":
        return IterChain(_value=iter([self.unwrap()])).repeat(n=n)

    def into_dict(self, n: int) -> "DictChain[int, T]":
        val: T = self.unwrap()
        return DictChain(_value={i: val for i in range(n)})

    def into_dict_iter[K](self, n: int, *keys: K) -> "DictChain[K, IterChain[T]]":
        val: IterChain[T] = self.into_iter(n=n)
        return DictChain(_value={k: val for k in keys})


@dataclass(slots=True, frozen=True, repr=False)
class IterChain[V](BaseIterChain[V]):
    @property
    def get(self) -> Getter[V]:
        return Getter(_value=self.unwrap())

    def agg[V1](self, on: lf.AggFunc[V, V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=on(self.unwrap()))

    def into_dict(self) -> "DictChain[int, V]":
        return DictChain(_value={i: v for i, v in enumerate(self.unwrap())})

    def into_dict_iter[K](self, n: int) -> "DictChain[int, IterChain[V]]":
        return DictChain(_value={k: self for k in range(n)})

    def into_dict_iter_with_keys[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        return DictChain(_value={k: self for k in keys})

    def into_groups[K](
        self, on: lf.TransformFunc[V, K]
    ) -> "DictChain[K, IterChain[V]]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self.unwrap())
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def into_reduced_groups[K](
        self, key: lf.TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.unwrap()))

    def into_frequencies(self) -> "DictChain[V, int]":
        return DictChain(_value=cz.itertoolz.frequencies(self.unwrap()))


@dataclass(slots=True, frozen=True, repr=False)
class DictChain[K, V](BaseDictChain[K, V]):
    @property
    def get_key(self) -> Getter[K]:
        return Getter(_value=self.unwrap().keys())

    @property
    def get_value(self) -> Getter[V]:
        return Getter(_value=self.unwrap().values())

    @property
    def get_item(self) -> Getter[tuple[K, V]]:
        return Getter(_value=self.unwrap().items())

    def agg_keys[K1](self, on: lf.AggFunc[K, K1]) -> ScalarChain[K1]:
        return ScalarChain(_value=on(self.unwrap().keys()))

    def agg_values[V1](self, on: lf.AggFunc[V, V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=on(self.unwrap().values()))

    def agg_items[V1](self, on: lf.AggFunc[tuple[K, V], V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=on(self.unwrap().items()))

    def into_iter_keys(self) -> "IterChain[K]":
        return IterChain(_value=self.unwrap().keys())

    def into_iter_values(self) -> IterChain[V]:
        return IterChain(_value=self.unwrap().values())

    def into_iter_items(self) -> IterChain[tuple[K, V]]:
        return IterChain(_value=self.unwrap().items())
