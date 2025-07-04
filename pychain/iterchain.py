import operator as op
from collections.abc import Callable, Iterable
from typing import Self, Any
from dataclasses import dataclass
import cytoolz as cz
import polars as pl


@dataclass(slots=True, frozen=True)
class ScalarChain[V]:
    value: V

    @classmethod
    def _new(cls, value: V) -> Self:
        return cls(value)

    @classmethod
    def _transform(cls, value: object) -> Self:
        return cls(value)  # type: ignore

    def compose[V1](self, *fns: Callable[[V], V1]) -> Self:
        return self._transform(value=cz.functoolz.compose_left(*fns)(self.value))

    def pipe[V1](self, *fns: Callable[..., V1]) -> Self:
        return self._transform(value=cz.functoolz.pipe(data=self.value, *fns))

    def thread_first[V1](self, *fns: Callable[..., V1]) -> Self:
        return self._transform(value=cz.functoolz.thread_first(val=self.value, *fns))

    def thread_last[V1](
        self, *fns: tuple[Callable[..., V1], Any] | Callable[..., V1]
    ) -> Self:
        return self._transform(value=cz.functoolz.thread_last(val=self.value, *fns))

    def to_int(self) -> "NumericChain[int]":
        if not isinstance(self.value, (int, float)):
            raise TypeError(f"Cannot convert {type(self.value)} to int")
        return NumericChain(value=int(self.value))

    def to_float(self) -> "NumericChain[float]":
        if not isinstance(self.value, (int, float)):
            raise TypeError(f"Cannot convert {type(self.value)} to float")
        return NumericChain(value=float(self.value))

    def to_string(self) -> str:
        return str(self.value)

    def into_iter(self) -> "IterChain[V]":
        return IterChain(value=iter([self.value]))


@dataclass(slots=True, frozen=True)
class NumericChain[V: int | float](ScalarChain[V]):
    def add(self, other: V) -> Self:
        return self._new(value=op.add(self.value, other))

    def sub(self, other: V) -> Self:
        return self._new(value=op.sub(self.value, other))

    def mul(self, other: V) -> Self:
        return self._new(value=op.mul(self.value, other))

    def div(self, other: float | int) -> "NumericChain[float]":
        return NumericChain(value=op.truediv(self.value, other))

    def abs(self) -> "NumericChain[float]":
        return NumericChain(value=abs(self.value))

    def round(self, ndigits: int) -> "NumericChain[float]":
        return NumericChain(value=round(number=self.value, ndigits=ndigits))


@dataclass(slots=True, frozen=True)
class IterChain[V]:
    value: Iterable[V]

    @classmethod
    def _new(cls, value: Iterable[V]) -> Self:
        return cls(value)

    def _to_scalar[V1](self, f: Callable[[Iterable[V]], V1]) -> ScalarChain[V1]:
        return ScalarChain(value=f(self.value))

    def _to_numeric[V1: int | float](
        self, f: Callable[[Iterable[V]], V1]
    ) -> NumericChain[V1]:
        return NumericChain(value=f(self.value))

    @classmethod
    def range(cls, start: int, stop: int, step: int = 1) -> "IterChain[int]":
        return IterChain(value=range(start, stop, step))

    def enumerate(self) -> "IterChain[tuple[int, V]]":
        return IterChain(value=enumerate(iterable=self.value))

    def copy(self) -> Self:
        return self._new(value=self.value)

    def map[V1](self, f: Callable[[V], V1]) -> "IterChain[V1]":
        return IterChain(value=map(f, self.value))

    def flat_map[V1](self, f: Callable[[V], Iterable[V1]]) -> "IterChain[V1]":
        return IterChain(value=cz.itertoolz.concat(map(f, self.value)))

    def filter(self, f: Callable[[V], bool]) -> Self:
        return self._new(value=filter(f, self.value))

    def iterate(self, f: Callable[[V], V], arg: V) -> Self:
        return self._new(value=cz.itertoolz.iterate(func=f, x=arg))

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        return self._new(value=cz.itertoolz.accumulate(f, self.value))

    def concat(self, *others: Iterable[V]) -> Self:
        return self._new(value=cz.itertoolz.concat([self.value, *others]))

    def flatten(self) -> Self:
        return self._new(value=cz.itertoolz.concat(self.value))

    def cons(self, value: V) -> Self:
        return self._new(value=cz.itertoolz.cons(value, self.value))

    def head(self, n: int) -> Self:
        # NOTE: immutable -> cz.itertoolz.peekn
        return self._new(value=cz.itertoolz.take(n, self.value))

    def tail(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.tail(n, self.value))

    def drop_first(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.drop(n, self.value))

    def every(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.take_nth(n, self.value))

    def repeat(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.concat(map(lambda x: [x] * n, self.value)))

    def unique(self) -> Self:
        return self._new(value=cz.itertoolz.unique(self.value))

    def cumsum(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.add, self.value))

    def cumprod(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.mul, self.value))

    def isdistinct(self) -> bool:
        return cz.itertoolz.isdistinct(seq=self.value)

    def len(self) -> NumericChain[int]:
        return self._to_numeric(f=cz.itertoolz.count)

    def first(self) -> ScalarChain[V]:
        # NOTE: immutable -> cz.itertoolz.peek
        return self._to_scalar(f=cz.itertoolz.first)

    def second(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.second)

    def last(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.last)

    def sum(self) -> NumericChain[V]:  # type: ignore
        return self._to_numeric(f=sum)  # type: ignore

    def min(self) -> NumericChain[V]:  # type: ignore
        return self._to_numeric(f=min)  # type: ignore

    def max(self) -> NumericChain[V]:  # type: ignore
        return self._to_numeric(f=max)  # type: ignore

    def to_list(self) -> list[V]:
        return list(self.value)

    def to_tuple(self) -> tuple[V, ...]:
        return tuple(self.value)

    def to_series(self, name: str | None = None) -> pl.Series:
        return pl.Series(name=name, values=self.value)

    def to_lazy_dict[K](self, *keys: K) -> "IterDictChain[K, V]":
        return IterDictChain(values={k: self.copy() for k in keys})


@dataclass(slots=True, frozen=True)
class DictChain[K, V]:
    values: dict[K, V]

    def _new(self, value: dict[K, V]) -> Self:
        return self.__class__(value)

    def _transform[K1, V1](self, value: dict[K1, V1]) -> "DictChain[K1, V1]":
        return self.__class__(value)  # type: ignore

    def keys_to_iter(self) -> IterChain[K]:
        return IterChain(value=self.values.keys())

    def values_to_iter(self) -> IterChain[V]:
        return IterChain(value=self.values.values())

    def map_items[K1, V1](
        self, f: Callable[[tuple[K, V]], tuple[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return self._transform(value=cz.dicttoolz.itemmap(f, self.values))

    def map_keys[K1](self, f: Callable[[K], K1]) -> "DictChain[K1, V]":
        return self._transform(value=cz.dicttoolz.keymap(f, self.values))

    def map_values[V1](self, f: Callable[[V], V1]) -> "DictChain[K, V1]":
        return self._transform(value=cz.dicttoolz.valmap(f, self.values))

    def select_and_filter(self, predicate: Callable[[tuple[K, V]], bool]) -> Self:
        return self._new(value=cz.dicttoolz.itemfilter(predicate, self.values))

    def select(self, predicate: Callable[[K], bool]) -> Self:
        return self._new(value=cz.dicttoolz.keyfilter(predicate, self.values))

    def filter(self, predicate: Callable[[V], bool]) -> Self:
        return self._new(value=cz.dicttoolz.valfilter(predicate, self.values))

    def get(self, key: K) -> V | None:
        return self.values.get(key)

    def drop(self, *keys: K) -> Self:
        return self._new(value=cz.dicttoolz.dissoc(d=self.values, *keys))

    def with_key(self, key: K, value: V) -> Self:
        return self._new(value=cz.dicttoolz.assoc(self.values, key, value))

    def stack(self, *others: dict[K, V]) -> Self:
        return self._new(value=cz.dicttoolz.merge(self.values, *others))

    def to_pl(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.values)

    def to_pl_lazy(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.values)

    def to_dict(self) -> dict[K, V]:
        return self.values


@dataclass(slots=True, frozen=True)
class IterDictChain[K, V](DictChain[K, IterChain[V]]):
    values: dict[K, IterChain[V]]

    def collect(self) -> dict[K, list[V]]:
        return self.map_values(f=lambda x: x.to_list()).values
