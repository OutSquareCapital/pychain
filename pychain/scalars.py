import operator as op
from collections.abc import Callable
from dataclasses import dataclass
from typing import Self, Any

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

    def to_list(self) -> list[T]:
        return [self.value]

    def to_tuple(self) -> tuple[T, ...]:
        return (self.value,)


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
