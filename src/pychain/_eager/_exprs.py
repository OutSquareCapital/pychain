from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Concatenate

import cytoolz.functoolz as ft


@dataclass(slots=True)
class BasePipe[T](ABC):
    obj: T

    @abstractmethod
    def do(self, func: Any) -> Any:
        raise NotImplementedError

    def compose(self, *funcs: Callable[[T], T]):
        return self.__class__(ft.compose_left(self.obj, *funcs))  # type: ignore

    def unwrap(self):
        return self.obj


@dataclass(slots=True)
class Pipe[T](BasePipe[T]):
    obj: T

    def do[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ) -> "Pipe[R]":
        return Pipe(func(self.obj, *args, **kwargs))
