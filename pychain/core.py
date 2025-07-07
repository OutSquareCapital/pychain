import functools as ft
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

import cytoolz as cz
import functional as fn  # type: ignore
import polars as pl

import pychain.lazyfuncs as lf


@dataclass(slots=True, frozen=True)
class BaseChain[T](ABC):
    """
    # BaseChain class
    BaseChain is an abstract base class that provides a framework for creating a chainable, lazy evaluation pipeline
    for processing data.

    The class maintain an internal generic value `_value` and a list of processing functions `_pipeline`.

    ## from

    If the method starts with "from_", it is considered a factory function.
    They are available either as the public function at the lib level, or as a class method.

    ## lazy

    Most of the methods are lazy evaluated, so when they are called, they will just add the function to the pipeline, and return the current instance.

    ## with

    If the method starts with "with_", it is considered a transformation function.
    Henceforth, it will collect internally the function, before returning a new instance of the class with the transformed value.

    ## to

    If the method starts with "to_", it is considered a terminal function that will go out of the current class.
    It may return a new instance of another pychain class, a python built-in type, or another library type.

    ## check

    If the method starts with "check_", it is considered a check function.
    It will return a boolean value indicating whether the condition is met for the current value.
    """

    _value: T
    _pipeline: list[lf.ProcessFunc[T]] = field(
        default_factory=list[lf.ProcessFunc[T]], init=False
    )

    def do(self, f: lf.ProcessFunc[T]) -> Self:
        """Adds a same-type lazy function to the pipeline."""
        self._pipeline.append(f)
        return self

    #TODO: trouver meilleur nom pour cette méthode
    @abstractmethod
    def transform[T1](self, f: Callable[[T], Any]) -> Any:
        """
        Applies a transformation function to the current value.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def pipe(self, *fns: lf.ProcessFunc[T]) -> Self:
        """Adds a composed lazy function to the pipeline by combining multiple functions."""
        return self.do(f=(cz.functoolz.compose_left(*fns)))

    def thread_first(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-first' manner."""
        return self.do(f=ft.partial(lf.thread_first, fns=fns))

    def thread_last(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-last' manner."""
        return self.do(f=ft.partial(lf.thread_last, fns=fns))

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
