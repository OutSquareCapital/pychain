import functools as ft
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Self

import cytoolz as cz

from ... import _fn
from ..._protocols import ProcessFunc, ThreadFunc


@dataclass(slots=True, frozen=True, repr=False)
class AbstractChain[T]:
    _value: T
    _pipeline: list[Callable[[T], Any]] = field(default_factory=list[ProcessFunc[T]])

    def __repr__(self) -> str:
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    def do(self, f: ProcessFunc[T]) -> Self:
        """
        Add a function to the pipeline. Returns self for chaining.

        Example:
            >>> chain = AbstractChain([1, 2, 3]).do(sum)
            >>> chain.unwrap()
            6
        """
        self._pipeline.append(f)
        return self

    def thread_first(self, *fns: ThreadFunc[T]) -> Self:
        """
        Thread value as first argument through functions (see cytoolz.thread_first).

        Example:
        >>> def add(x: int, y: int) -> int:
        ...     return x + y
        >>> def pow(x: int, y: int) -> int:
        ...     return x**y
        >>> chain = AbstractChain(1).thread_first((add, 4), (pow, 2))
        >>> chain.unwrap()
        25
        """
        return self.do(f=ft.partial(_fn.thread_first, fns=fns))

    def thread_last(self, *fns: ThreadFunc[T]) -> Self:
        """
        Thread value as last argument through functions (see cytoolz.thread_last).

        Example:
            >>> chain = AbstractChain([1, 2, 3]).thread_last(
            ...     (map, lambda x: x + 1), sum
            ... )
            >>> chain.unwrap()
            9
        """
        return self.do(f=ft.partial(_fn.thread_last, fns=fns))

    def clone(self) -> Self:
        """
        Return a deep copy of the chain and its pipeline.
        """
        return self.__class__(deepcopy(self._value), deepcopy(self._pipeline))

    def unwrap(self) -> T:
        """
        Execute the pipeline on the value and return the result.
        If pipeline is empty, return the value.

        Example:
            >>> chain = AbstractChain([1, 2, 3]).do(sum)
            >>> chain.unwrap()
            6
        """
        if not self._pipeline:
            return self._value
        return cz.functoolz.pipe(self._value, *self._pipeline)
