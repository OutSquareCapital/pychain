import operator as op
from collections.abc import Callable, Iterable
from typing import Self
from dataclasses import dataclass
import cytoolz as cz

from pychain.scalars import ScalarChain, NumericChain


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
    ) -> NumericChain[U]:
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

    def to_list(self) -> list[T]:
        return list(self.value)

    def to_tuple(self) -> tuple[T, ...]:
        return tuple(self.value)
