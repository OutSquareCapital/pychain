from __future__ import annotations

import itertools
from collections.abc import Callable, Collection, Generator, Iterable, Iterator
from typing import Any, Concatenate

import cytoolz as cz

from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._dicts import BaseDict
from ._eager import BaseEager
from ._filters import BaseFilter
from ._groups import BaseGroups
from ._joins import BaseJoins
from ._lists import BaseList
from ._maps import BaseMap
from ._partitions import BasePartitions
from ._process import BaseProcess
from ._rolling import BaseRolling
from ._tuples import BaseTuples


class Iter[T](
    BaseAgg[T],
    BaseBool[T],
    BaseFilter[T],
    BaseProcess[T],
    BaseMap[T],
    BaseRolling[T],
    BaseList[T],
    BaseTuples[T],
    BasePartitions[T],
    BaseJoins[T],
    BaseGroups[T],
    BaseEager[T],
    BaseDict[T],
):
    """
    A wrapper around Python's built-in Iterators/Generators types, providing a rich set of functional programming tools.

    It's designed around lazy evaluation, allowing for efficient processing of large datasets.

    - To instantiate from a lazy Iterator/Generator, simply pass it to the standard constructor.
    - To instantiate from an eager Collection (like a list or set), use the `from_` class method.
    """

    __slots__ = ("_data",)

    def __init__(self, data: Iterator[T] | Generator[T, Any, Any]) -> None:
        self._data = data

    @staticmethod
    def from_count(start: int = 0, step: int = 1) -> Iter[int]:
        """
        Create an infinite iterator of evenly spaced values.

        **Warning** ⚠️
            This creates an infinite iterator.
            Be sure to use `Iter.take()` or `Iter.slice()` to limit the number of items taken.

        Args:
            start: Starting value of the sequence. Defaults to 0.
            step: Difference between consecutive values. Defaults to 1.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_count(10, 2).take(3).into(list)
        [10, 12, 14]

        ```
        """

        return Iter(itertools.count(start, step))

    @staticmethod
    def from_func[U](func: Callable[[U], U], input: U) -> Iter[U]:
        """
        Create an infinite iterator by repeatedly applying a function on an original input.

        **Warning** ⚠️
            This creates an infinite iterator.
            Be sure to use `Iter.take()` or `Iter.slice()` to limit the number of items taken.

        Args:
            func: Function to apply repeatedly.
            input: Initial value to start the iteration.

        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_func(lambda x: x + 1, 0).take(3).into(list)
        [0, 1, 2]

        ```
        """

        return Iter(cz.itertoolz.iterate(func, input))

    @staticmethod
    def from_[U](data: Iterable[U] | U, *more_data: U) -> Iter[U]:
        """
        Create an iterator from any Iterable, or from unpacked values.

        - An Iterable is any object capable of returning its members one at a time, permitting it to be iterated over in a for-loop.
        - An Iterator is an object representing a stream of data; returned by calling `iter()` on an Iterable.
        - Once an Iterator is exhausted, it cannot be reused or reset.

        If you need to reuse the data, consider collecting it into a list first with `.collect()`.

        In general, avoid intermediate references when dealing with lazy iterators, and prioritize method chaining instead.

        Args:
            data: Iterable to convert into an iterator, or a single value.
            more_data: Additional values to include if 'data' is not an Iterable.
        Example:
        ```python
        >>> import pyochain as pc
        >>> data: tuple[int, ...] = (1, 2, 3)
        >>> iterator = pc.Iter.from_(data)
        >>> iterator.unwrap().__class__.__name__
        'tuple_iterator'
        >>> mapped = iterator.map(lambda x: x * 2)
        >>> mapped.unwrap().__class__.__name__
        'map'
        >>> mapped.collect(tuple).unwrap()
        (2, 4, 6)
        >>> # iterator is now exhausted
        >>> iterator.collect().unwrap()
        []
        >>> # Creating from unpacked values
        >>> pc.Iter.from_(1, 2, 3).collect(tuple).unwrap()
        (1, 2, 3)

        ```
        """
        if cz.itertoolz.isiterable(data):
            return Iter(iter(data))
        else:
            d: Iterable[U] = (data, *more_data)  # type: ignore[assignment]
            return Iter(iter(d))

    @staticmethod
    def unfold[S, V](seed: S, generator: Callable[[S], tuple[V, S] | None]) -> Iter[V]:
        """
        Create an iterator by repeatedly applying a generator function to an initial state.

        The `generator` function takes the current state and must return:

        - A tuple `(value, new_state)` to emit the `value` and continue with the `new_state`.
        - `None` to stop the generation.

        This is functionally equivalent to a state-based `while` loop.

        **Warning** ⚠️
            If the `generator` function never returns `None`, it creates an infinite iterator.
            Be sure to use `Iter.take()` or `Iter.slice()` to limit the number of items taken if necessary.

        Args:
            seed: Initial state for the generator.
            generator: Function that generates the next value and state.

        Example:
        ```python
        >>> import pyochain as pc
        >>> # Example 1: Simple counter up to 5
        >>> def counter_generator(state: int) -> tuple[int, int] | None:
        ...     if state < 5:
        ...         return (state * 10, state + 1)
        ...     return None
        >>> pc.Iter.unfold(seed=0, generator=counter_generator).into(list)
        [0, 10, 20, 30, 40]
        >>> # Example 2: Fibonacci sequence up to 100
        >>> type FibState = tuple[int, int]
        >>> def fib_generator(state: FibState) -> tuple[int, FibState] | None:
        ...     a, b = state
        ...     if a > 100:
        ...         return None
        ...     return (a, (b, a + b))
        >>> pc.Iter.unfold(seed=(0, 1), generator=fib_generator).into(list)
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        >>> # Example 3: Infinite iterator (requires take())
        >>> pc.Iter.unfold(seed=1, generator=lambda s: (s, s * 2)).take(5).into(list)
        [1, 2, 4, 8, 16]

        ```
        """
        from ._main import Iter

        def _unfold() -> Iterator[V]:
            current_seed: S = seed
            while True:
                result: tuple[V, S] | None = generator(current_seed)
                if result is None:
                    break
                value, next_seed = result
                yield value
                current_seed = next_seed

        return Iter(_unfold())

    def itr[**P, R, U: Iterable[Any]](
        self: Iter[U],
        func: Callable[Concatenate[Iter[U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to each element after wrapping it in an Iter.

        This is a convenience method for the common pattern of mapping a function over an iterable of iterables.

        Args:
            func: Function to apply to each wrapped element.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        Example:
        ```python
        >>> import pyochain as pc
        >>> data = [
        ...     [1, 2, 3],
        ...     [4, 5],
        ...     [6, 7, 8, 9],
        ... ]
        >>> pc.Iter.from_(data).itr(
        ...     lambda x: x.repeat(2).flatten().reduce(lambda a, b: a + b)
        ... ).into(list)
        [12, 18, 60]

        ```
        """

        def _itr(data: Iterable[U]) -> Generator[R, None, None]:
            return (func(Iter(iter(x)), *args, **kwargs) for x in data)

        return self.apply(_itr)


class Seq[T](BaseAgg[T], BaseEager[T]):
    """
    pyochain.Seq represent an in memory collection.

    Provides a subset of pyochain.Iter methods with eager evaluation, and is the return type of pyochain.Iter.collect().
    """

    __slots__ = ("_data",)

    def __init__(self, data: Collection[T]) -> None:
        self._data = data

    @staticmethod
    def from_[U](data: Collection[U] | U, *more_data: U) -> Seq[U]:
        """
        Create a Seq from a collection or unpacked values.

        Args:
            data: Collection of items or a single item.
            more_data: Additional item to include if 'data' is not a collection.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Seq.from_([1, 2, 3]).unwrap()
        [1, 2, 3]
        >>> pc.Seq.from_(1, 2).unwrap()
        (1, 2)

        ```

        """
        if cz.itertoolz.isiterable(data):
            return Seq(data)
        else:
            return Seq((data, *more_data))

    def iter(self) -> Iter[T]:
        """
        Get an iterator over the sequence.
        Call this to switch to lazy evaluation.
        """
        return Iter(iter(self.unwrap()))
