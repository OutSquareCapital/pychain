import operator as op
from collections.abc import Callable, Iterable
from typing import Self, Any
from dataclasses import dataclass
import cytoolz as cz


@dataclass(slots=True, frozen=True)
class ScalarChain[T]:
    value: T

    def _new(self, value: T) -> Self:
        return self.__class__(value)

    def _transform[U](self, value: U) -> "ScalarChain[U]":
        return self.__class__(value)  # type: ignore

    def compose[U](self, *fns: Callable[[T], U]) -> "ScalarChain[U]":
        return self._transform(value=cz.functoolz.compose_left(*fns)(self.value))

    def pipe[U](self, *fns: Callable[..., U]) -> "ScalarChain[U]":
        return self._transform(value=cz.functoolz.pipe(data=self.value, *fns))

    def thread_first[U](self, *fns: Callable[..., U]) -> "ScalarChain[U]":
        return self._transform(value=cz.functoolz.thread_first(val=self.value, *fns))

    def thread_last[U](
        self, *fns: tuple[Callable[..., U], Any] | Callable[..., U]
    ) -> "ScalarChain[U]":
        return self._transform(value=cz.functoolz.thread_last(val=self.value, *fns))

    def to_int(self) -> "NumericChain[int]":
        return NumericChain(_value=int(self.value))  # type: ignore

    def to_float(self) -> "NumericChain[float]":
        return NumericChain(_value=float(self.value))  # type: ignore

    def to_string(self) -> str:
        return str(self.value)

    def to_list(self) -> "IterChain[T]":
        return IterChain(value=[self.value])

    def to_tuple(self) -> "IterChain[T]":
        return IterChain(value=(self.value,))


@dataclass(slots=True, frozen=True)
class NumericChain[T: int | float](ScalarChain[T]):
    def add(self, other: T) -> Self:
        return self._new(value=op.add(self.value, other))

    def sub(self, other: T) -> Self:
        return self._new(value=op.sub(self.value, other))

    def mul(self, other: T) -> Self:
        return self._new(value=op.mul(self.value, other))

    def div(self, other: float | int) -> Self:
        return self._new(value=op.truediv(self.value, other))

    def abs(self) -> "NumericChain[float]":
        return NumericChain(value=abs(self.value))

    def round(self, ndigits: int) -> "NumericChain[float]":
        return NumericChain(value=round(number=self.value, ndigits=ndigits))


@dataclass(slots=True, frozen=True)
class IterChain[T]:
    value: Iterable[T]

    def _new(self, value: Iterable[T]) -> Self:
        return self.__class__(value)

    def _transform[U](self, value: Iterable[U]) -> "IterChain[U]":
        return self.__class__(value)  # type: ignore

    def _to_scalar[U](self, f: Callable[[Iterable[T]], U]) -> ScalarChain[U]:
        return ScalarChain(value=f(self.value))

    def _to_numeric[U: int | float](
        self, f: Callable[[Iterable[T]], U]
    ) -> "NumericChain[U]":
        return NumericChain(value=f(self.value))

    def map[U](self, f: Callable[[T], U]) -> "IterChain[U]":
        return self._transform(value=map(f, self.value))

    def flat_map[U](self, f: Callable[[T], Iterable[U]]) -> "IterChain[U]":
        return self._transform(value=cz.itertoolz.concat(map(f, self.value)))

    def filter(self, f: Callable[[T], bool]) -> Self:
        return self._new(value=filter(f, self.value))

    def iterate(self, f: Callable[[T], T], arg: T) -> Self:
        return self._new(value=cz.itertoolz.iterate(func=f, x=arg))

    def accumulate(self, f: Callable[[T, T], T]) -> Self:
        return self._new(value=cz.itertoolz.accumulate(f, self.value))

    def concat(self, *others: Iterable[T]) -> Self:
        return self._new(value=cz.itertoolz.concat([self.value, *others]))

    def cons(self, value: T) -> Self:
        return self._new(value=cz.itertoolz.cons(value, self.value))

    def head(self, n: int) -> Self:
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

    def len(self) -> NumericChain[int]:
        return self._to_numeric(f=cz.itertoolz.count)

    def first(self) -> ScalarChain[T]:
        return self._to_scalar(f=cz.itertoolz.first)

    def second(self) -> ScalarChain[T]:
        return self._to_scalar(f=cz.itertoolz.second)

    def last(self) -> ScalarChain[T]:
        return self._to_scalar(f=cz.itertoolz.last)

    def isdistinct(self) -> bool:
        return cz.itertoolz.isdistinct(seq=self.value)

    def sum(self) -> NumericChain[T]:  # type: ignore
        return self._to_numeric(f=sum)  # type: ignore

    def collect(self) -> list[T]:
        return list(self.value)
