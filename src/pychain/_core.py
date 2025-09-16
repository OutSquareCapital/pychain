from __future__ import annotations

import pprint
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, NamedTuple, Protocol, Self

import cytoolz as cz

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter


class Peeked[T](NamedTuple):
    value: T | tuple[T, ...]
    sequence: Iterable[T]


class Pluckable[KT, VT](Protocol):
    def __getitem__(self, key: KT) -> VT: ...


class SupportsDunderLT[T](Protocol):
    def __lt__(self, other: T, /) -> bool: ...


class SupportsDunderGT[T](Protocol):
    def __gt__(self, other: T, /) -> bool: ...


class SupportsDunderLE[T](Protocol):
    def __le__(self, other: T, /) -> bool: ...


class SupportsDunderGE[T](Protocol):
    def __ge__(self, other: T, /) -> bool: ...


class SupportsAllComparisons(
    SupportsDunderLT[Any],
    SupportsDunderGT[Any],
    SupportsDunderLE[Any],
    SupportsDunderGE[Any],
    Protocol,
): ...


type SupportsRichComparison[T] = SupportsDunderLT[T] | SupportsDunderGT[T]


class CommonBase[T](ABC):
    """
    Base class for all wrappers.
    You can subclass this to create your own wrapper types.
    The pipe unwrap method must be implemented to allow piping functions that transform the underlying data type, whilst retaining the wrapper.
    """

    __slots__ = ("_data",)

    def __init__(self, data: T) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"{self._data.__repr__()}"

    def println(self, pretty: bool = True) -> Self:
        """
        Print the underlying data and return self for chaining.
        """
        if pretty:
            pprint.pprint(self._data)
        else:
            print(self._data)
        return self

    def _new(self, data: T) -> Self:
        return self.__class__(data)

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

    def pipe_unwrap[**P, R](
        self,
        func: Callable[Concatenate[T, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """
        Pipe the *unwrapped* underlying data into a function.

        This method is used to pass the raw data (e.g., the dict, list, or array) to a function,
        returning the function's result.

        The result is not wrapped.

        Example:
            >>> from pychain import Dict
            >>> Dict({"a": 1, "b": 2}).pipe_unwrap(
            ...     lambda d: {k: v + 1 for k, v in d.items()}
            ... )
            {'a': 2, 'b': 3}

        This is a terminal operation.
        """
        return func(self._data, *args, **kwargs)

    @abstractmethod
    def pipe_into[**P](
        self,
        func: Callable[Concatenate[Self, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        """
        Pipe the underlying data into a function, then wrap the result in the same wrapper type.

        Each pychain class implement this method to allow chaining of functions that transform the
        underlying data and return a new wrapped instance of the same subclass.

        Example:
            >>> from pychain import Dict
            >>> Dict({1: 2}).pipe_into(lambda d: {k: v + 1 for k, v in d.items()})
            {1: 3}

        Use this to keep the chainable API after applying a transformation to the data.
        """
        raise NotImplementedError

    def pipe_chain(self, *funcs: Callable[[T], T]) -> Self:
        """
        Pipe a value through a sequence of functions.

        Prefer this method over multiple pipe_into calls when the functions don't transform the underlying type.

        I.e. Iter(data).pipe_chain(f, g, h).unwrap() is equivalent to h(g(f(data)))

            >>> import pychain as pc
            >>> import numpy as np
            >>> data = np.array([1, 2, 3, 4, 5])
            >>> pc.Array(data).pipe_chain(lambda x: x + 2, lambda x: x * 3).pipe_into(
            ...     lambda x: x.clip(10, 20)
            ... )
            array([10, 12, 15, 18, 20])
        """
        return self._new(cz.functoolz.pipe(self._data, *funcs))


def iter_factory[T](data: Iterable[T]) -> Iter[T]:
    from ._iter import Iter

    return Iter(data)


def dict_factory[K, V](data: dict[K, V]) -> Dict[K, V]:
    from ._dict import Dict

    return Dict(data)
