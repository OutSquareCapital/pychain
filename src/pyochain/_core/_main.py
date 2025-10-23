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
        raise NotImplementedError

    def println(self, pretty: bool = True) -> Self:
        """
        Print the underlying data and return self for chaining.

        Useful for debugging, simply insert `.println()` in the chain,
        and then removing it will not affect the rest of the chain.
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
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(range(5)).into(list)
        [0, 1, 2, 3, 4]

        ```
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
        """
        Apply a function to the underlying iterable and return an Iter of the result.
        Allow to pass user defined functions that transform the iterable while retaining the Iter wrapper.
        Args:
            func: Function to apply to the underlying iterable.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Example:
        ```python
        >>> import pyochain as pc
        >>> def double(data: Iterable[int]) -> Iterator[int]:
        ...     return (x * 2 for x in data)
        >>> pc.Iter.from_([1, 2, 3]).apply(double).into(list)
        [2, 4, 6]
        """
        from .._iter import Iter

        return Iter(self.into(func, *args, **kwargs))

    def collect(self, factory: Callable[[Iterable[T]], Collection[T]] = list) -> Seq[T]:
        """
        Collect the elements into a sequence.
        Args:
            factory: A callable that takes an iterable and returns a collection. Defaults to list.

        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(range(5)).collect().unwrap()
        [0, 1, 2, 3, 4]

        ```
        """
        from .._iter import Seq

        return Seq(self.into(factory))


class MappingWrapper[K, V](CommonBase[dict[K, V]]):
    _data: dict[K, V]

    def apply[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[K, V], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[KU, VU]:
        """
        Apply a function to the underlying dict and return a Dict of the result.
        Allow to pass user defined functions that transform the dict while retaining the Dict wrapper.
        Args:
            func: Function to apply to the underlying dict.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        Example:
        ```python
        >>> import pyochain as pc
        >>> def invert_dict(d: dict[K, V]) -> dict[V, K]:
        ...     return {v: k for k, v in d.items()}
        >>> pc.Dict({'a': 1, 'b': 2}).apply(invert_dict).unwrap()
        {1: 'a', 2: 'b'}

        ```
        """
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
