from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Concatenate

import cytoolz as cz

from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._filters import BaseFilter
from ._lists import BaseList
from ._maps import BaseMap
from ._process import BaseProcess
from ._rolling import BaseRolling
from ._tuples import BaseTuples

if TYPE_CHECKING:
    from .._dict import Dict


class Iter[T](
    BaseAgg[T],
    BaseBool[T],
    BaseFilter[T],
    BaseProcess[T],
    BaseMap[T],
    BaseRolling[T],
    BaseList[T],
    BaseTuples[T],
):
    """
    A wrapper around Python's built-in iterable types, providing a rich set of functional programming tools.

    It supports lazy evaluation, allowing for efficient processing of large datasets.

    It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

    It can be constructed from any iterable, including `lists`, `tuples`, `sets`, and `generators`.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.unwrap().__repr__()})"

    @staticmethod
    def from_count(start: int = 0, step: int = 1) -> Iter[int]:
        """
        Create an infinite iterator of evenly spaced values.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> from pychain import Iter
        >>> Iter.from_count(10, 2).head(3).into(list)
        [10, 12, 14]
        """

        return Iter(itertools.count(start, step))

    @staticmethod
    def from_range(start: int, stop: int, step: int = 1) -> Iter[int]:
        """
        Create an iterator from a range.

        Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> from pychain import Iter
        >>> Iter.from_range(1, 5).into(list)
        [1, 2, 3, 4]
        """

        return Iter(range(start, stop, step))

    @staticmethod
    def from_func[U](func: Callable[[U], U], x: U) -> Iter[U]:
        """
        Create an infinite iterator by repeatedly applying a function into an original input x.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> from pychain import Iter
        >>> Iter.from_func(lambda x: x + 1, 0).head(3).into(list)
        [0, 1, 2]
        """

        return Iter(cz.itertoolz.iterate(func, x))

    @staticmethod
    def from_[U](*elements: U) -> Iter[U]:
        """
        Create an iterator from the given elements.

        >>> from pychain import Iter
        >>> Iter.from_(1, 2, 3).into(list)
        [1, 2, 3]
        """

        return Iter(elements)

    def into[**P, R](
        self,
        func: Callable[Concatenate[Iterable[T], P], R],
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

    def apply[**P, R](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        return Iter(self.into(func, *args, **kwargs))

    def reduce_by[K](
        self, key: Callable[[T], K], binop: Callable[[T, T], T]
    ) -> Iter[K]:
        """
        Perform a simultaneous groupby and reduction

        >>> from collections.abc import Iterable
        >>> import pychain as pc
        >>> from operator import add, mul
        >>>
        >>> def is_even(x: int) -> bool:
        ...     return x % 2 == 0
        >>>
        >>> def group_reduce(data: Iterable[int]) -> int:
        ...     return pc.Iter(data).reduce(add)
        >>>
        >>> data = pc.Iter([1, 2, 3, 4, 5])
        >>> data.reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> data.group_by(is_even).map_values(group_reduce).unwrap()
        {False: 9, True: 6}

        But the former does not build the intermediate groups, allowing it to operate in much less space.

        This makes it suitable for larger datasets that do not fit comfortably in memory

        Simple Examples
        >>> pc.Iter([1, 2, 3, 4, 5]).reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> pc.Iter([1, 2, 3, 4, 5]).reduce_by(is_even, mul).unwrap()
        {False: 15, True: 8}
        """

        return self.apply(partial(cz.itertoolz.reduceby, key, binop))

    def group_by[K](self, on: Callable[[T], K]) -> Dict[K, list[T]]:
        """
        Group elements by key function and return a Dict result.

        >>> from pychain import Iter

        >>> names = [
        ...     "Alice",
        ...     "Bob",
        ...     "Charlie",
        ...     "Dan",
        ...     "Edith",
        ...     "Frank",
        ... ]
        >>> Iter(names).group_by(len).sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
            3: ['Bob', 'Dan'],
            5: ['Alice', 'Edith', 'Frank'],
            7: ['Charlie'],
        )
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
        False: [1, 3, 5, 7],
        True: [2, 4, 6, 8],
        )

        Non-callable keys imply grouping on a member.

        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
        'F': [{'name': 'Alice', 'gender': 'F'}],
        'M': [{'name': 'Bob', 'gender': 'M'}, {'name': 'Charlie', 'gender': 'M'}],
        )
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.groupby, on)))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.

        >>> from pychain import Iter
        >>> Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies().unwrap()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        from .._dict import Dict

        return Dict(self.into(cz.itertoolz.frequencies))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function

        >>> from pychain import Iter
        >>> Iter(["cat", "mouse", "dog"]).count_by(len).unwrap()
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> Iter([1, 2, 3]).count_by(iseven).unwrap()
        {False: 2, True: 1}
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.recipes.countby, key)))

    def with_keys[K](self, keys: Iterable[K]) -> Dict[K, T]:
        """
        Create a Dict by zipping the iterable with keys.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_keys(["a", "b", "c"]).unwrap()
        {'a': 1, 'b': 2, 'c': 3}
        """
        from .._dict import Dict

        return Dict(dict(zip(keys, self.unwrap())))

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_values(["a", "b", "c"]).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}
        """
        from .._dict import Dict

        return Dict(dict(zip(self.unwrap(), values)))
