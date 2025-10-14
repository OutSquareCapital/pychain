from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, Self

import cytoolz as cz

if TYPE_CHECKING:
    from .._dict import Dict
    from .._iter import Iter


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

    def __repr__(self) -> str:
        return f"{self.unwrap().__repr__()}"

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

    def _new[**P](
        self, func: Callable[Concatenate[T, P], T], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        return self.__class__(func(self.unwrap(), *args, **kwargs))

    def unwrap(self) -> T:
        """
        Return the underlying data.

        This is a terminal operation.
        """
        return self._data

    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)

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

    def apply[**P](
        self,
        func: Callable[Concatenate[T, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """
        Pipe the underlying data into a function, then wrap the result in the same wrapper type.

        Each pychain class implement this method to allow chaining of functions that transform the
        underlying data and return a new wrapped instance of the same subclass.

            >>> from pychain import Iter
            >>> Iter.from_range(0, 5).apply(tuple).unwrap()
            (0, 1, 2, 3, 4)

        Use this to keep the chainable API after applying a transformation to the data.
        """
        return self.__class__.__call__(func(self.unwrap(), *args, **kwargs))

    def pipe_chain(self, *funcs: Callable[[T], T]) -> Self:
        """
        Pipe a value through a sequence of functions.

        Prefer this method over multiple apply calls when the functions don't transform the underlying type.

        I.e. Wrapper(data).pipe_chain(f, g, h).unwrap() is equivalent to h(g(f(data)))

        >>> Wrapper(5).pipe_chain(lambda x: x + 2, lambda x: x * 3, lambda x: x - 4)
        17
        """
        return self._new(cz.functoolz.pipe, *funcs)


class IterWrapper[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]


class Wrapper[T](CommonBase[T]):
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
        return Wrapper(func(self.unwrap(), *args, **kwargs))

    def to_iter[U: Iterable[Any]](self: Wrapper[U]) -> Iter[U]:
        """
        Convert the wrapped data to an Iter wrapper.
        """
        from .._iter import Iter

        return self.into(Iter)

    def to_dict[KU, VU](self: Wrapper[dict[KU, VU]]) -> Dict[KU, VU]:
        """
        Convert the wrapped dict to a Dict wrapper.

            >>> import pychain as pc
            >>>
            >>> data = {1: "a", 2: "b"}
            >>>
            >>> pc.Wrapper(data).to_dict().unwrap()
            {1: 'a', 2: 'b'}
        """
        from .._dict import Dict

        return self.into(Dict)
