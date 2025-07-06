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
    The execution strategy is the following:

    ### Case "do":
        If the function return the same type as the current value(ProcessFunc), it is added to the pipeline (lazy evaluation, same instance).
    ### Case "transform":
        If the function returns a different type(TransformFunc), the pipeline is collected, the transformation is applied, and a new instance of the class is created with the transformed value(eager evaluation, new instance, new type).
    ### Case "_new":
        - If the value itself is an iterable(lazy value in itself), we create a new instance of the class with the new value.
    """

    _value: T
    _pipeline: list[lf.ProcessFunc[T]] = field(
        default_factory=list[lf.ProcessFunc[T]], init=False
    )

    @classmethod
    def _new(cls, value: T) -> Self:
        """Creates a new instance of the class with the given value."""
        return cls(value)

    @lf.lazy
    def do(self, f: lf.ProcessFunc[T]) -> Self:
        """Adds a same-type lazy function to the pipeline."""
        self._pipeline.append(f)
        return self

    @abstractmethod
    def transform[T1](self, f: Callable[[T], Any]) -> Any:
        """
        Applies a transformation function to the current value.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @lf.lazy
    def pipe(self, *fns: lf.ProcessFunc[T]) -> Self:
        """Adds a composed lazy function to the pipeline by combining multiple functions."""
        return self.do(f=(cz.functoolz.compose_left(*fns)))

    @lf.lazy
    def thread_first(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-first' manner."""
        return self.do(f=ft.partial(lf.thread_first, fns=fns))

    @lf.lazy
    def thread_last(self, *fns: lf.ThreadFunc[T]) -> Self:
        """Adds a lazy function to the pipeline that threads the value through the functions in a 'thread-last' manner."""
        return self.do(f=ft.partial(lf.thread_last, fns=fns))

    def unwrap(self) -> T:
        """Collects the current value by applying all functions in the pipeline and returns the final value."""
        return self.collect()._value

    def collect(self) -> Self:
        """Applies all functions in the pipeline to the current value and returns a new instance of the class."""
        if not self._pipeline:
            return self
        return self.__class__(_value=cz.functoolz.pipe(self._value, *self._pipeline))

    def to_series(self) -> pl.Series:
        """Converts the current value to a Polars Series."""
        return pl.Series(values=self.unwrap())

    def to_frame(self) -> pl.DataFrame:
        """Converts the current value to a Polars DataFrame."""
        return pl.DataFrame(data=self.unwrap())

    def to_lazy_frame(self) -> pl.LazyFrame:
        """Converts the current value to a Polars LazyFrame."""
        return pl.LazyFrame(data=self.unwrap())

    def to_functional(self):
        """Converts the current value to a functional sequence using the `fn` library."""
        return fn.seq(self.unwrap())
