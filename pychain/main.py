import operator as op
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Self

import cytoolz as cz
from pychain.scalars import Aggregator


@dataclass(slots=True, frozen=True)
class LazyStream[T]:
    _data: Iterable[T]

    def _new(self, data: Iterable[T]) -> Self:
        return self.__class__(data)

    def _transform[U](self, data: Iterable[U]) -> "LazyStream[U]":
        return self.__class__(data)  # type: ignore

    def map[U](self, f: Callable[[T], U]) -> "LazyStream[U]":
        return self._transform(map(f, self._data))

    def flat_map[U](self, f: Callable[[T], Iterable[U]]) -> "LazyStream[U]":
        return self._transform(cz.itertoolz.concat(map(f, self._data)))

    def filter(self, f: Callable[[T], bool]) -> Self:
        return self._new(data=filter(f, self._data))

    def iterate(self, f: Callable[[T], T], arg: T) -> Self:
        return self._new(cz.itertoolz.iterate(func=f, x=arg))

    def accumulate(self, f: Callable[[T, T], T]) -> Self:
        return self._new(cz.itertoolz.accumulate(f, self._data))

    def concat(self, *others: Iterable[T]) -> Self:
        return self._new(cz.itertoolz.concat([self._data, *others]))

    def cons(self, value: T) -> Self:
        return self._new(cz.itertoolz.cons(value, self._data))

    def head(self, n: int) -> Self:
        return self._new(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        return self._new(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        return self._new(cz.itertoolz.drop(n, self._data))

    def every(self, n: int) -> Self:
        return self._new(cz.itertoolz.take_nth(n, self._data))

    def unique(self) -> Self:
        return self._new(cz.itertoolz.unique(self._data))

    def cumsum(self) -> Self:
        return self._new(cz.itertoolz.accumulate(op.add, self._data))

    def cumprod(self) -> Self:
        return self._new(cz.itertoolz.accumulate(op.mul, self._data))

    @property
    def scalar(self) -> Aggregator[T]:
        return Aggregator(_parent=self._data)

    def to_list(self) -> list[T]:
        return list(self._data)

    def to_tuple(self) -> tuple[T, ...]:
        return tuple(self._data)
