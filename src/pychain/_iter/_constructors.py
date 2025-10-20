from __future__ import annotations

import itertools
from collections.abc import Callable, Iterator
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

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> import pychain as pc
        >>> pc.Iter.from_count(10, 2).head(3).into(list)
        [10, 12, 14]
        """
        from ._main import Iter

        return Iter(itertools.count(start, step))

    @staticmethod
    def from_range(start: int, stop: int, step: int = 1) -> Iter[int]:
        """
        Create an iterator from a range.

        Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> import pychain as pc
        >>> pc.Iter.from_range(1, 5).into(list)
        [1, 2, 3, 4]
        """
        from ._main import Iter

        return Iter(range(start, stop, step))

    @staticmethod
    def from_func[U](func: Callable[[U], U], x: U) -> Iter[U]:
        """
        Create an infinite iterator by repeatedly applying a function into an original input x.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> import pychain as pc
        >>> pc.Iter.from_func(lambda x: x + 1, 0).head(3).into(list)
        [0, 1, 2]
        """
        from ._main import Iter

        return Iter(cz.itertoolz.iterate(func, x))

    @staticmethod
    def from_[U](*elements: U) -> Iter[U]:
        """
        Create an iterator from the given elements.

        >>> import pychain as pc
        >>> pc.Iter.from_(1, 2, 3).into(list)
        [1, 2, 3]
        """
        from ._main import Iter

        return Iter(elements)

    @staticmethod
    def unfold[S, V](seed: S, generator: Callable[[S], tuple[V, S] | None]) -> Iter[V]:
        """
        Create an iterator by repeatedly applying a generator function to an initial state (seed).

        The `generator` function takes the current state and must return:
        - A tuple `(value, new_state)` to emit the `value` and continue with the `new_state`.
        - `None` to stop the generation.

        This is functionally equivalent to a state-based `while` loop.

        **Warning** ⚠️
            If the `generator` function never returns `None`, it creates an infinite iterator.
            Be sure to use `Iter.head()` or `Iter.slice()` to limit the number of items taken if necessary.

        >>> import pychain as pc
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

        >>> # Example 3: Infinite iterator (requires head())
        >>> pc.Iter.unfold(seed=1, generator=lambda s: (s, s * 2)).head(5).into(list)
        [1, 2, 4, 8, 16]
        """
        from ._main import Iter

        def _generate() -> Iterator[V]:
            current_seed: S = seed
            while True:
                result: tuple[V, S] | None = generator(current_seed)
                if result is None:
                    break
                value, next_seed = result
                yield value
                current_seed = next_seed

        return Iter(_generate())
