import functools as ft
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self
from copy import deepcopy

import cytoolz as cz

import src.pychain.lazyfuncs as lf


@dataclass(slots=True, frozen=True, repr=False)
class AbstractChain[T]:
    _value: T
    _pipeline: list[Callable[[T], Any]] = field(default_factory=list[lf.ProcessFunc[T]])

    def __repr__(self) -> str:
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    def do(self, f: lf.ProcessFunc[T]) -> Self:
        self._pipeline.append(f)
        return self

    def into(self, f: lf.TransformFunc[T, Any]):
        return self.__class__(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )

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
