from dataclasses import dataclass
from collections.abc import Callable, Iterable
import functools as ft
import cytoolz as cz
import polars as pl
import functional as fn  # type: ignore
import numpy as np
from numpy.typing import NDArray
from typing import TYPE_CHECKING, Any
from src.lazyfuncs import TransformFunc, CheckFunc

if TYPE_CHECKING:
    from src.implementations import ScalarChain


@dataclass(slots=True, frozen=True)
class GetterBase[V]:
    _value: Iterable[V]

    def __call__[V1](self, f: TransformFunc[Iterable[V], V1]) -> "ScalarChain[V1]":
        raise NotImplementedError

    def first(self) -> "ScalarChain[V]":
        return self(f=cz.itertoolz.first)

    def second(self) -> "ScalarChain[V]":
        return self(f=cz.itertoolz.second)

    def last(self) -> "ScalarChain[V]":
        return self(f=cz.itertoolz.last)

    def at_index(self, index: int) -> "ScalarChain[V]":
        return self(f=ft.partial(cz.itertoolz.nth, n=index))

    def len(self) -> "ScalarChain[int]":
        return self(f=cz.itertoolz.count)


@dataclass(slots=True, frozen=True)
class Checker[V]:
    _value: Iterable[V]

    def __call__[V1](self, f: CheckFunc[Iterable[V]]) -> bool:
        return f(self._value)

    def all(self) -> bool:
        return all(self._value)

    def any(self) -> bool:
        return any(self._value)

    def distinct(self) -> bool:
        return cz.itertoolz.isdistinct(self._value)

    def iterable(self) -> bool:
        return cz.itertoolz.isiterable(self._value)


@dataclass(slots=True, frozen=True)
class Converter[V]:
    _value: Iterable[V]

    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> Any:
        return f(self._value)

    def list(self) -> list[V]:
        return list(self._value)

    def set(self) -> set[V]:
        return set(self._value)

    def tuple(self) -> tuple[V, ...]:
        return tuple(self._value)

    def array(self) -> NDArray[Any]:
        return np.array(self._value)

    def series(self) -> pl.Series:
        return pl.Series(values=self._value)

    def dataframe(self) -> pl.DataFrame:
        return pl.DataFrame(data=self._value)

    def lazyframe(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self._value)

    def functional(self):
        return fn.seq(self._value)
