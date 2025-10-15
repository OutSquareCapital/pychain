from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, Self

if TYPE_CHECKING:
    pass


class CommonBase[T](ABC):
    """
    Base class for all wrappers.
    You can subclass this to create your own wrapper types.
    The pipe unwrap method must be implemented to allow piping functions that transform the underlying data type, whilst retaining the wrapper.
    """

    _data: T

    __slots__ = ("_data",)

    def __init__(self, data: T) -> None:
        self._data = data

    @abstractmethod
    def _new[**P](
        self, func: Callable[Concatenate[T, P], T], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        raise NotImplementedError

    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)

    @abstractmethod
    def apply[**P](
        self,
        func: Callable[Concatenate[T, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        """
        Pipe the underlying data into a function, then wrap the result in the same wrapper type.

        Each pychain class implement this method to allow chaining of functions that transform the
        underlying data and return a new wrapped instance of the same subclass.

            >>> from pychain import Iter
            >>> Iter.from_range(0, 5).apply(tuple).unwrap()
            (0, 1, 2, 3, 4)

        Use this to keep the chainable API after applying a transformation to the data.
        """
        raise NotImplementedError


class EagerWrapper[T](CommonBase[T]):
    def _new[**P](
        self, func: Callable[Concatenate[T, P], T], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        return self.__class__(func(self.unwrap(), *args, **kwargs))

    def _display_(self) -> T:
        """Display method specific for Marimo."""
        return self.unwrap()

    def println(self, pretty: bool = True) -> Self:
        """
        Print the underlying data and return self for chaining.

        Useful for debugging, simply insert `.println()` in the chain, and then removing it will not affect the rest of the chain.
        """
        from pprint import pprint

        if pretty:
            pprint(self.unwrap())
        else:
            print(self.unwrap())
        return self

    def unwrap(self) -> T:
        """
        Return the underlying data.

        This is a terminal operation.
        """
        return self._data

    def into[**P, R](
        self,
        func: Callable[Concatenate[T, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """
        Pass the *unwrapped* underlying data into a function.

        The result is not wrapped.

            >>> from pychain import Iter
            >>> Iter.from_range(0, 5).into(tuple)
            (0, 1, 2, 3, 4)

        This is a core functionality that allows ending the chain whilst keeping the code style consistent.
        """
        return func(self.unwrap(), *args, **kwargs)


class IterWrapper[T](EagerWrapper[Iterable[T]]):
    _data: Iterable[T]


class Wrapper[T](EagerWrapper[T]):
    """
    A generic Wrapper for any type.
    The pipe into method is implemented to return a Wrapper of the result type.

    This class is intended for use with other types/implementations that do not support the fluent/functional style.
    This allow the use of a consistent code style across the code base.
    """

    def apply[**P, R](
        self,
        func: Callable[Concatenate[T, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Wrapper[R]:
        """
        Pipe the underlying data into a function, then wrap the result in a new `Wrapper` instance.

        Note that if the generic type `R` is itself a generic type, the resulting `Wrapper` will not retain that information in some cases.

        This is a limitation of Python's type system for generics.

        This is also why pipe into is an abstract method in `CommonBase`, altough `Dict` and `Iter` have the exact same implementation.
        """
        return Wrapper(self.into(func, *args, **kwargs))
