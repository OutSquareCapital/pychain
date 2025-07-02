import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import partial
from typing import Self

import cytoolz as cz


@dataclass(slots=True, frozen=True)
class ScalarStream[T]:
    _value: T
    _pipe: list[Callable[..., T]]

    def _append(self, f: Callable[..., T]) -> Self:
        self._pipe.append(f)
        return self

    def _transform[U](self, f: Callable[..., U]) -> "ScalarStream[U]":
        self._pipe.append(f)  # type: ignore
        return self.__class__(self._value, self._pipe)  # type: ignore

    def compose[U](self, *fns: Callable[[T], U]) -> "ScalarStream[U]":
        return self._transform(cz.functoolz.compose_left(*fns))

    def add(self, value: T) -> Self:
        return self._append(partial(self._add, b=value))

    def sub(self, value: T) -> Self:
        return self._append(partial(self._sub, b=value))

    def mul(self, value: T) -> Self:
        return self._append(partial(self._mul, b=value))

    def div(self, value: T) -> "ScalarStream[float]":
        return self._transform(partial(self._div, b=value))

    def abs(self) -> "ScalarStream[float]":
        return self._transform(abs)

    def round(self, ndigits: int) -> "ScalarStream[float]":
        return self._transform(partial(round, ndigits=ndigits))

    @staticmethod
    def _add(a: T, b: T) -> T:
        return op.add(a, b)

    @staticmethod
    def _sub(a: T, b: T) -> T:
        return op.sub(a, b)

    @staticmethod
    def _mul(a: T, b: T) -> T:
        return op.mul(a, b)

    @staticmethod
    def _div(a: T, b: T) -> float:
        return op.truediv(a, b)

    def collect(self) -> T:
        return cz.functoolz.pipe(self._value, *self._pipe)

    def to_list(self) -> list[T]:
        return [self.collect()]

    def to_tuple(self) -> tuple[T, ...]:
        return (self.collect(),)


@dataclass(slots=True, frozen=True)
class Aggregator[T]:
    _parent: Iterable[T]

    def _to_scalar[U](self, f: Callable[[Iterable[T]], U]) -> ScalarStream[U]:
        return ScalarStream(_value=f(self._parent), _pipe=[])

    def len(self) -> ScalarStream[int]:
        return self._to_scalar(cz.itertoolz.count)

    def first(self) -> ScalarStream[T]:
        return self._to_scalar(cz.itertoolz.first)

    def second(self) -> ScalarStream[T]:
        return self._to_scalar(cz.itertoolz.second)

    def last(self) -> ScalarStream[T]:
        return self._to_scalar(cz.itertoolz.last)

    def isdistinct(self) -> bool:
        return cz.itertoolz.isdistinct(self._parent)

    def sum(self) -> ScalarStream[T]:
        return ScalarStream(_value=sum(self._parent), _pipe=[])  # type: ignore
