from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING

import cytoolz as cz

if TYPE_CHECKING:
    from ._main import Iter


class IterConstructors:
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
        from ._main import Iter

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
        from ._main import Iter

        return Iter(cz.itertoolz.iterate(func, input))

    @staticmethod
    def from_[U](data: Iterable[U]) -> Iter[U]:
        """
        Create an iterator from any Iterable.

        - An Iterable is any object capable of returning its members one at a time, permitting it to be iterated over in a for-loop.
        - An Iterator is an object representing a stream of data; returned by calling `iter()` on an Iterable.
        - Once an Iterator is exhausted, it cannot be reused or reset.

        If you need to reuse the data, consider collecting it into a list first with `.collect()`.

        In general, avoid intermediate references when dealing with lazy iterators, and prioritize method chaining instead.
        Args:
            data: Iterable to convert into an iterator.
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

        ```
        """
        from ._main import Iter

        return Iter(iter(data))

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
