import operator as op
from collections.abc import Callable, Iterable
from typing import Self, Any
from dataclasses import dataclass
import cytoolz as cz
import polars as pl
from copy import deepcopy
from pychain.interfaces import RandomProtocol, CheckFunc, lazy


@dataclass(slots=True, frozen=True)
class ScalarTransformator[V]:
    _parent: "ScalarChain[V]"

    @property
    def value(self) -> V:
        return self._parent.value

    def copy(self) -> "ScalarChain[V]":
        return deepcopy(self._parent)

    def series(self) -> pl.Series:
        return pl.Series(values=self.value)

    def frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.value)

    @lazy
    def lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.value)

    def dict[K](self, *keys: K) -> "DictChain[K, ScalarChain[V]]":
        return DictChain(values={k: self.copy() for k in keys})

    def int(self) -> "ScalarChain[int]":
        return ScalarChain(value=int(self.value))  # type: ignore

    def float(self) -> "ScalarChain[float]":
        return ScalarChain(value=float(self.value))  # type: ignore

    def string(self) -> "ScalarChain[str]":
        return ScalarChain(value=str(self.value))

    @lazy
    def iter(self) -> "IterChain[V]":
        return IterChain(value=iter([self.value]))


@dataclass(slots=True, frozen=True)
class IterTransformator[V]:
    _parent: "IterChain[V]"

    @property
    def value(self) -> Iterable[V]:
        return self._parent.value

    def copy(self) -> "IterChain[V]":
        return deepcopy(self._parent)

    def list(self) -> list[V]:
        return list(self.value)

    def tuple(self) -> tuple[V, ...]:
        return tuple(self.value)

    def series(self) -> pl.Series:
        return pl.Series(values=self.value)

    def frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.value)

    @lazy
    def lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.value)

    def lazy_dict[K](self, *keys: K) -> "IterDictChain[K, V]":
        return IterDictChain(values={k: self.copy() for k in keys})


@dataclass(slots=True, frozen=True)
class DictTransformator[K, V]:
    _parent: "DictChain[K, V]"

    @property
    def values(self) -> dict[K, V]:
        return self._parent.values

    @lazy
    def keys_to_iter(self) -> "IterChain[K]":
        return IterChain(value=self.values.keys())

    @lazy
    def values_to_iter(self) -> "IterChain[V]":
        return IterChain(value=self.values.values())

    def series(self) -> pl.Series:
        return pl.Series(values=self.values)

    def frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.values)

    @lazy
    def lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.values)

    def dict(self) -> dict[K, V]:
        return self.values

    def value(self, key: K) -> V | None:
        return self.values.get(key)


@dataclass(slots=True, frozen=True)
class ScalarChain[V]:
    value: V

    @classmethod
    def _new(cls, value: V) -> Self:
        return cls(value)

    @property
    def to(self) -> ScalarTransformator[V]:
        return ScalarTransformator(_parent=self)

    def compose[V1](self, *fns: Callable[[V], V1]) -> "ScalarChain[V1]":
        return ScalarChain(value=cz.functoolz.compose_left(*fns)(self.value))

    def pipe[V1](self, *fns: Callable[..., V1]) -> "ScalarChain[V1]":
        return ScalarChain(value=cz.functoolz.pipe(data=self.value, *fns))

    def thread_first[V1](self, *fns: Callable[..., V1]) -> "ScalarChain[V1]":
        return ScalarChain(value=cz.functoolz.thread_first(val=self.value, *fns))

    def thread_last[V1](
        self, *fns: tuple[Callable[..., V1], Any] | Callable[..., V1]
    ) -> "ScalarChain[V1]":
        return ScalarChain(value=cz.functoolz.thread_last(val=self.value, *fns))

    def add(self, other: V) -> Self:
        return self._new(value=op.add(self.value, other))

    def sub(self, other: V) -> Self:
        return self._new(value=op.sub(self.value, other))

    def mul(self, other: V) -> Self:
        return self._new(value=op.mul(self.value, other))

    def div(self, other: float | int) -> "ScalarChain[float]":
        return ScalarChain(value=op.truediv(self.value, other))

    def abs(self) -> Self:
        return self._new(value=abs(self.value))  # type: ignore

    def round(self, ndigits: int) -> Self:
        return self._new(value=round(number=self.value, ndigits=ndigits))  # type: ignore


@dataclass(slots=True, frozen=True)
class IterChain[V]:
    value: Iterable[V]

    @classmethod
    def _new(cls, value: Iterable[V]) -> Self:
        return cls(value)

    def _to_scalar[V1](self, f: Callable[[Iterable[V]], V1]) -> ScalarChain[V1]:
        return ScalarChain(value=f(self.value))

    @property
    def to(self) -> IterTransformator[V]:
        return IterTransformator(_parent=self)

    def range(
        self, start: int = 0, stop: int | None = None, step: int = 1
    ) -> "IterChain[int]":
        return IterChain(value=range(start, stop or self.len().value, step))

    @lazy
    def enumerate(self) -> "IterChain[tuple[int, V]]":
        return IterChain(value=enumerate(iterable=self.value))

    @lazy
    def map[V1](self, f: Callable[[V], V1]) -> "IterChain[V1]":
        return IterChain(value=map(f, self.value))

    @lazy
    def flatten[V1](self, f: Callable[[V], Iterable[V1]]) -> "IterChain[V1]":
        return IterChain(value=cz.itertoolz.concat(map(f, self.value)))

    @lazy
    def interleave(self, *others: Iterable[V]) -> Self:
        return self._new(value=cz.itertoolz.interleave([self.value, *others]))

    @lazy
    def interpose(self, element: V) -> Self:
        return self._new(value=cz.itertoolz.interpose(el=element, seq=self.value))

    @lazy
    def diff(
        self, *seqs: Iterable[V], key: Callable[[V], V] | None = None
    ) -> "IterChain[tuple[V, ...]]":
        return IterChain(value=cz.itertoolz.diff(self.value, *seqs, key=key))

    @lazy
    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        return self._new(value=cz.itertoolz.topk(k=n, seq=self.value, key=key))

    @lazy
    def random_sample(
        self, probability: float, state: RandomProtocol | int | None = None
    ) -> Self:
        return self._new(
            value=cz.itertoolz.random_sample(
                prob=probability, seq=self.value, random_state=state
            )
        )

    def partition(self, n: int, pad: V | None = None) -> "IterChain[tuple[V, ...]]":
        return IterChain(value=cz.itertoolz.partition(n=n, seq=self.value, pad=pad))

    def partition_all(self, n: int) -> "IterChain[tuple[V, ...]]":
        return IterChain(value=cz.itertoolz.partition_all(n=n, seq=self.value))

    def rolling(self, length: int) -> "IterChain[tuple[V, ...]]":
        return IterChain(value=cz.itertoolz.sliding_window(n=length, seq=self.value))

    @lazy
    def concat(self, *others: Iterable[V]) -> Self:
        return self._new(value=cz.itertoolz.concat([self.value, *others]))

    @lazy
    def filter(self, f: CheckFunc[V]) -> Self:
        return self._new(value=filter(f, self.value))

    @lazy
    def iterate(self, f: Callable[[V], V], arg: V) -> Self:
        return self._new(value=cz.itertoolz.iterate(func=f, x=arg))

    @lazy
    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        return self._new(value=cz.itertoolz.accumulate(f, self.value))

    @lazy
    def cons(self, value: V) -> Self:
        return self._new(value=cz.itertoolz.cons(value, self.value))

    @lazy
    def peek(self) -> Self:
        val, _ = cz.itertoolz.peek(self.value)
        print(f"Peeked value: {val}")
        return self

    @lazy
    def peekn(self, n: int) -> Self:
        values, _ = cz.itertoolz.peekn(n, self.value)
        print(f"Peeked {n} values: {list(values)}")
        return self

    @lazy
    def head(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.take(n, self.value))

    @lazy
    def tail(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.tail(n, self.value))

    @lazy
    def drop_first(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.drop(n, self.value))

    @lazy
    def every(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.take_nth(n, self.value))

    @lazy
    def repeat(self, n: int) -> Self:
        return self._new(value=cz.itertoolz.concat(map(lambda x: [x] * n, self.value)))

    @lazy
    def unique(self) -> Self:
        return self._new(value=cz.itertoolz.unique(self.value))

    @lazy
    def cumsum(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.add, self.value))

    @lazy
    def cumprod(self) -> Self:
        return self._new(value=cz.itertoolz.accumulate(op.mul, self.value))

    def isdistinct(self) -> bool:
        return cz.itertoolz.isdistinct(seq=self.value)

    def len(self) -> ScalarChain[int]:
        return self._to_scalar(f=cz.itertoolz.count)

    def first(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.first)

    def second(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.second)

    def last(self) -> ScalarChain[V]:
        return self._to_scalar(f=cz.itertoolz.last)

    def sum(self) -> ScalarChain[V]:  # type: ignore
        return self._to_scalar(f=sum)  # type: ignore

    def min(self) -> ScalarChain[V]:  # type: ignore
        return self._to_scalar(f=min)  # type: ignore

    def max(self) -> ScalarChain[V]:  # type: ignore
        return self._to_scalar(f=max)  # type: ignore

    def group_by[K](self, on: Callable[[V], K]) -> "IterDictChain[K, V]":
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self.value)
        return IterDictChain(values={k: IterChain(v) for k, v in grouped.items()})

    def reduce_by[K](
        self, key: Callable[[V], K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        return DictChain(values=cz.itertoolz.reduceby(key, binop, self.value))

    def frequencies(self) -> "DictChain[V, int]":
        return DictChain(values=cz.itertoolz.frequencies(self.value))


@dataclass(slots=True, frozen=True)
class DictChain[K, V]:
    values: dict[K, V]

    def _new(self, value: dict[K, V]) -> Self:
        return self.__class__(value)

    @property
    def to(self) -> DictTransformator[K, V]:
        return DictTransformator(_parent=self)

    def map_items[K1, V1](
        self, f: Callable[[tuple[K, V]], tuple[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return DictChain(values=cz.dicttoolz.itemmap(func=f, d=self.values))

    def map_keys[K1](self, f: Callable[[K], K1]) -> "DictChain[K1, V]":
        return DictChain(values=cz.dicttoolz.keymap(func=f, d=self.values))

    def map_values[V1](self, f: Callable[[V], V1]) -> "DictChain[K, V1]":
        return DictChain(values=cz.dicttoolz.valmap(func=f, d=self.values))

    def merge_with[V1](self, f: Callable[..., V1], *others: dict[K, V]) -> "DictChain[K, V1]":
        return DictChain(values=cz.dicttoolz.merge_with(f, self.values, *others))

    def select_and_filter(self, predicate: Callable[[tuple[K, V]], bool]) -> Self:
        return self._new(value=cz.dicttoolz.itemfilter(predicate, self.values))

    def select(self, predicate: CheckFunc[K]) -> Self:
        return self._new(value=cz.dicttoolz.keyfilter(predicate, self.values))

    def filter(self, predicate: CheckFunc[V]) -> Self:
        return self._new(value=cz.dicttoolz.valfilter(predicate, self.values))

    def drop(self, *keys: K) -> Self:
        return self._new(value=cz.dicttoolz.dissoc(d=self.values, *keys))

    def with_key(self, key: K, value: V) -> Self:
        return self._new(value=cz.dicttoolz.assoc(self.values, key, value))

    def stack(self, *others: dict[K, V]) -> Self:
        return self._new(value=cz.dicttoolz.merge(self.values, *others))

    def update_in(self, *keys: K, f: Callable[..., V]) -> Self:
        return self._new(value=cz.dicttoolz.update_in(d=self.values, keys=keys, func=f))

@dataclass(slots=True, frozen=True)
class IterDictChain[K, V](DictChain[K, IterChain[V]]):
    values: dict[K, IterChain[V]]

    def collect(self) -> dict[K, list[V]]:
        return self.map_values(f=lambda x: x.to.list()).values
