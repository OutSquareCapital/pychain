from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Concatenate, Self

if TYPE_CHECKING:
    from .._dict import Dict
    from .._iter import Iter, Seq


class Pipeable:
    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)


class CommonBase[T](ABC, Pipeable):
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
        >>> import pychain as pc
        >>> from collections.abc import Iterable, Iterator
        >>> def add_one(data: Iterable[int]) -> Iterator[int]:
        ...     return (x + 1 for x in data)
        >>> pc.Iter.from_([1, 2, 3, 4]).apply(add_one).collect().unwrap()
        [2, 3, 4, 5]

        Use this to keep the chainable API after applying a transformation to the data.
        """
        raise NotImplementedError

    def println(self, pretty: bool = True) -> Self:
        """
        Print the underlying data and return self for chaining.

        Useful for debugging, simply insert `.println()` in the chain, and then removing it will not affect the rest of the chain.
        """
        from pprint import pprint

        if pretty:
            pprint(self.unwrap(), sort_dicts=False)
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

        >>> import pychain as pc
        >>> pc.Iter.from_(range(5)).into(list)
        [0, 1, 2, 3, 4]

        This is a core functionality that allows ending the chain whilst keeping the code style consistent.
        """
        return func(self.unwrap(), *args, **kwargs)


class IterWrapper[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def apply[**P, R](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterator[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        from .._iter import Iter

        return Iter(self.into(func, *args, **kwargs))

    def collect(self, factory: Callable[[Iterable[T]], Collection[T]] = list) -> Seq[T]:
        from .._iter import Seq

        return Seq(self.into(factory))


class MappingWrapper[K, V](CommonBase[dict[K, V]]):
    _data: dict[K, V]

    def _new[**P](
        self,
        func: Callable[Concatenate[dict[K, V], P], dict[K, V]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        return self.__class__(self.into(func, *args, **kwargs))

    def apply[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[K, V], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[KU, VU]:
        from .._dict import Dict

        return Dict(self.into(func, *args, **kwargs))


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
        return Wrapper(self.into(func, *args, **kwargs))
