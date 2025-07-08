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
    """
    # BaseChain class
    BaseChain is an abstract base class that provides a framework for creating a chainable, lazy evaluation pipeline
    for processing data.

    ## Attributes
    - `_value`: The initial value of the chain, which can be of any type.
    - `_pipeline`: A list of functions that will be applied to the value in a lazy manner.

    ## Methods
    Most of the methods are lazy evaluated, so when they are called, they will just add the function to the pipeline, and return the current instance.

    However, if a method name start in one of the following ways, you can expect a specific behavior:

    ### from

        Considered a factory function.
        They are available either as the public function at the lib level, or as a class method.

    ### apply

        Considered a transformation function.
        Henceforth, it will collect internally the function, before returning a new instance of the class with the transformed value.

    ### to

        Considered a terminal function that will go out of the current class.
        It may return a new instance of another pychain class, a python built-in type, or another library type.

    ### is

        Considered a check function.
        It will return a boolean value indicating whether the condition is met for the current value.
    """

    _value: T
    _pipeline: list[Callable[[T], Any]] = field(default_factory=list[lf.ProcessFunc[T]])

    def __repr__(self) -> str:
        pipeline_repr: str = ",\n".join(f"{str(f)}" for f in self._pipeline)
        return f"class {self.__class__.__name__}(value={self._value},pipeline:[\n{pipeline_repr}\n])"

    def lazy(self, f: lf.ProcessFunc[T]) -> Self:
        """Adds a same-type lazy function to the pipeline."""
        self._pipeline.append(f)
        return self

    @abstractmethod
    def apply[T1](self, f: Callable[[T], Any]) -> Any:
        """
        Applies a transformation function to the current value.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def compose(self, *fns: lf.ProcessFunc[T]) -> Self:
        """Adds a composed lazy function to the pipeline by combining multiple functions."""
        return self.lazy(f=(cz.functoolz.compose_left(*fns)))

    def thread_first(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-first' manner."""
        return self.lazy(f=ft.partial(lf.thread_first, fns=fns))

    def thread_last(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-last' manner."""
        return self.lazy(f=ft.partial(lf.thread_last, fns=fns))

    def clone(self) -> Self:
        return self.__class__(deepcopy(self._value), deepcopy(self._pipeline))

    def to_unwrap(self) -> T:
        """
        Returns the final value.

        If the pipeline is empty, returns the current instance value.

        Otherwise, applies all functions in the pipeline to the current value and returns a new instance of the class.
        """
        if not self._pipeline:
            return self._value
        return cz.functoolz.pipe(self._value, *self._pipeline)

    def to_series(self) -> pl.Series:
        return pl.Series(values=self.to_unwrap())

    def to_frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.to_unwrap())

    def to_lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.to_unwrap())

    def to_functional(self):
        return fn.seq(self.to_unwrap())
