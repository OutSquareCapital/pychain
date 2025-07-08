import functools as ft
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self
from copy import deepcopy

import cytoolz as cz
import functional as fn  # type: ignore
import polars as pl

import pychain.lazyfuncs as lf


@dataclass(slots=True, frozen=True, repr=False)
class BaseChain[T](ABC):
    _value: T
    _pipeline: list[Callable[[T], Any]] = field(default_factory=list[lf.ProcessFunc[T]])

    def __repr__(self) -> str:
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    def do(self, f: lf.ProcessFunc[T]) -> Self:
        self._pipeline.append(f)
        return self

    @abstractmethod
    def do_as[T1](self, f: Callable[[T], Any]) -> Any:
        raise NotImplementedError

    def compose(self, *fns: lf.ProcessFunc[T]) -> Self:
        return self.do(f=(cz.functoolz.compose_left(*fns)))

    def thread_first(self, *fns: lf.ThreadFunc[T]) -> Self:
        return self.do(f=ft.partial(lf.thread_first, fns=fns))

    def thread_last(self, *fns: lf.ThreadFunc[T]) -> Self:
        return self.do(f=ft.partial(lf.thread_last, fns=fns))

    def clone(self) -> Self:
        return self.__class__(deepcopy(self._value), deepcopy(self._pipeline))

    def unwrap(self) -> T:
        if not self._pipeline:
            return self._value
        return cz.functoolz.pipe(self._value, *self._pipeline)

    def to_series(self) -> pl.Series:
        return pl.Series(values=self.unwrap())

    def to_frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.unwrap())

    def to_lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.unwrap())

    def to_functional(self):
        return fn.seq(self.unwrap())
