from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Concatenate, final

import cytoolz as cz

from .._executors import Executor

if TYPE_CHECKING:
    from ._dict import Dict


@final
class Iter[T](Executor[T]):
    """
    A wrapper around Python's built-in iterable types, providing a rich set of functional programming tools.

    It supports lazy evaluation, allowing for efficient processing of large datasets.

    It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

    It can be constructed from any iterable, including `lists`, `tuples`, `sets`, and `generators`.
    """

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

    def pluck(self, key: int | str | list[int] | list[str]) -> Iter[T]:
        """
        ``plucks`` an element or several elements from each item in a sequence.

        ``pluck`` maps itertoolz.get over a sequence and returns one or more elements of each item in the sequence.

        >>> from pychain import Iter
        >>> data = [{"id": 1, "name": "Cheese"}, {"id": 2, "name": "Pies"}]
        >>> Iter(data).pluck("name").into(list)
        ['Cheese', 'Pies']
        >>> Iter([[1, 2, 3], [4, 5, 7]]).pluck([0, 1]).into(list)
        [(1, 2), (4, 5)]
        """
        return self.apply(partial(cz.itertoolz.pluck, key))

    def reduce_by[K](
        self,
        key: Callable[[T], K],
        binop: Callable[[T, T], T],
        init: Any = "__no__default__",
    ) -> Iter[K]:
        """
        Perform a simultaneous groupby and reduction

        >>> data = Iter([1, 2, 3, 4, 5])
        >>> data.reduce_by(lambda x: x % 2 == 0, lambda x, y: x + y, 0).unwrap()
        {False: 9, True: 6}
        >>> data.group_by(lambda x: x % 2 == 0).map_values(
        ...     lambda group: Iter(group).reduce(lambda x, y: x + y)
        ... ).unwrap()
        {False: 9, True: 6}

        But the former does not build the intermediate groups, allowing it to operate in much less space.

        This makes it suitable for larger datasets that do not fit comfortably in memory

        The init keyword argument is the default initialization of the reduction.

        This can be either a constant value like 0 or a callable like lambda : 0 as might be used in defaultdict.

        Simple Examples

        >>> from operator import add, mul
        >>> Iter([1, 2, 3, 4, 5]).reduce_by(lambda x: x % 2 == 0, add).unwrap()
        {False: 9, True: 6}
        >>> Iter([1, 2, 3, 4, 5]).reduce_by(lambda x: x % 2 == 0, mul).unwrap()
        {False: 15, True: 8}

        Complex Example

        >>> projects = [
        ...     {"name": "build roads", "state": "CA", "cost": 1000000},
        ...     {"name": "fight crime", "state": "IL", "cost": 100000},
        ...     {"name": "help farmers", "state": "IL", "cost": 2000000},
        ...     {"name": "help farmers", "state": "CA", "cost": 200000},
        ... ]
        >>> Iter(projects).reduce_by(
        ...     "state",
        ...     lambda acc, x: acc + x["cost"],
        ...     0,
        ... ).unwrap()
        {'CA': 1200000, 'IL': 2100000}

        Example Using init

        >>> def set_add(s, i):
        ...     s.add(i)
        ...     return s
        >>> Iter([1, 2, 3, 4, 1, 2, 3]).reduce_by(lambda x: x % 2 == 0, set_add, set)
        {False: {1, 3}, True: {2, 4}}
        """

        return self.apply(partial(cz.itertoolz.reduceby, key, binop, init=init))

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
            3, list: ['Bob', 'Dan'],
            5, list: ['Alice', 'Edith', 'Frank'],
            7, list: ['Charlie'],
        )
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict(
            False, list: [1, 3, 5, 7],
            True, list: [2, 4, 6, 8],
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
            'F', list: [{'name': 'Alice', 'gender': 'F'}],
            'M', list: [{'name': 'Bob', 'gender': 'M'}, {'name': 'Charlie', 'gender': 'M'}],
        )
        """
        from ._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.groupby, on)))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.

        >>> from pychain import Iter
        >>> Iter(["cat", "cat", "ox", "pig", "pig", "cat"]).frequencies().unwrap()
        {'cat': 3, 'ox': 1, 'pig': 2}
        """
        from ._dict import Dict

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
        from ._dict import Dict

        return Dict(self.into(partial(cz.recipes.countby, key)))

    def with_keys[K](self, keys: Iterable[K]) -> Dict[K, T]:
        """
        Create a Dict by zipping the iterable with keys.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_keys(["a", "b", "c"]).unwrap()
        {'a': 1, 'b': 2, 'c': 3}
        """
        from ._dict import Dict

        return Dict(dict(zip(keys, self.unwrap())))

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).with_values(["a", "b", "c"]).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}
        """
        from ._dict import Dict

        return Dict(dict(zip(self.unwrap(), values)))
