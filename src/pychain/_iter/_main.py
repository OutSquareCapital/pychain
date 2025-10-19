from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Concatenate

import cytoolz as cz

from .._core import SupportsRichComparison
from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._constructors import IterConstructors
from ._filters import BaseFilter
from ._lists import BaseList
from ._maps import BaseMap
from ._partitions import BasePartitions
from ._process import BaseProcess
from ._rolling import BaseRolling
from ._transfos import BaseTransfos
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
    BasePartitions[T],
    BaseTransfos[T],
    IterConstructors,
):
    """
    A wrapper around Python's built-in iterable types, providing a rich set of functional programming tools.

    It supports lazy evaluation, allowing for efficient processing of large datasets.

    It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

    It can be constructed from any iterable, including `lists`, `tuples`, `sets`, and `generators`.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.unwrap().__repr__()})"

    def itr[**P, R, U: Iterable[Any]](
        self: Iter[U],
        func: Callable[Concatenate[Iter[U], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to each element after wrapping it in an Iter.
        Meant for when working with iterables of iterables.
        This is a convenience method for the common pattern of mapping a function over an iterable of iterables.
        >>> import pychain as pc
        >>> data = [
        ...     [1, 2, 3],
        ...     [4, 5],
        ...     [6, 7, 8, 9],
        ... ]
        >>> pc.Iter(data).itr(
        ...     lambda x: x.repeat(2).explode().reduce(lambda a, b: a + b)
        ... ).into(list)
        [12, 18, 60]
        """
        return self.map(lambda x: func(Iter(x), *args, **kwargs))

    def struct[**P, R, K, V](
        self: Iter[dict[K, V]],
        func: Callable[Concatenate[Dict[K, V], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
                Apply a function to each element after wrapping it in a Dict.
                Meant for when working with iterables of dictionaries.
                This is a convenience method for the common pattern of mapping a function over an iterable of dictionaries.
        >>> from typing import Any
        >>> import pychain as pc

        >>> data: list[dict[str, Any]] = [
        ...     {"name": "Alice", "age": 30, "city": "New York"},
        ...     {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ...     {"name": "Charlie", "age": 35, "city": "New York"},
        ...     {"name": "David", "age": 40, "city": "Paris"},
        ... ]


        >>> def to_title(d: pc.Dict[str, Any]) -> pc.Dict[str, Any]:
        ...     return d.map_keys(lambda k: k.title())
        >>> def is_young(d: pc.Dict[str, Any]) -> bool:
        ...     return d.unwrap().get("Age", 0) < 30
        >>> def set_continent(d: pc.Dict[str, Any], value: str) -> dict[str, Any]:
        ...     return d.with_key("Continent", value).unwrap()
        >>> pc.Iter(data).struct(to_title).filter_false(is_young).map(
        ...     lambda d: d.drop("Age").with_key("Continent", "NA")
        ... ).map_if(
        ...     lambda d: d.unwrap().get("City") == "Paris",
        ...     lambda d: set_continent(d, "Europe"),
        ...     lambda d: set_continent(d, "America"),
        ... ).group_by(lambda d: d.get("Continent")).map_values(
        ...     lambda d: pc.Iter(d)
        ...     .struct(lambda d: d.drop("Continent").unwrap())
        ...     .into(list)
        ... ).unwrap()
        {'America': [{'Name': 'Alice', 'City': 'New York'}, {'Name': 'Charlie', 'City': 'New York'}], 'Europe': [{'Name': 'David', 'City': 'Paris'}]}


        """
        from .._dict import Dict

        return self.map(lambda x: func(Dict(x), *args, **kwargs))

    def sort[U: SupportsRichComparison[Any]](
        self: Iter[U], reverse: bool = False
    ) -> Iter[U]:
        """
        Sort the elements of the sequence.
        Note: This method must consume the entire iterable to perform the sort.

        The result is a new iterable over the sorted sequence.

        >>> from pychain import Iter
        >>> Iter([3, 1, 2]).sort().into(list)
        [1, 2, 3]
        """
        return self._new(partial(sorted, reverse=reverse))

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
        Dict({
            3: ['Bob', 'Dan'],
            5: ['Alice', 'Edith', 'Frank'],
            7: ['Charlie']
        })
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            False: [1, 3, 5, 7],
            True: [2, 4, 6, 8]
        })

        Non-callable keys imply grouping on a member.

        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> Iter(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            'F': [
                {'name': 'Alice', 'gender': 'F'}
            ],
            'M': [
                {'name': 'Bob', 'gender': 'M'},
                {'name': 'Charlie', 'gender': 'M'}
            ]
        })
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


        >>> import pychain as pc
        >>> keys = ["a", "b", "c"]
        >>> values = [1, 2, 3]
        >>> pc.Iter(values).with_keys(keys).unwrap()
        {'a': 1, 'b': 2, 'c': 3}

        This is equivalent to:
        >>> pc.Iter(keys).zip(values).pipe(lambda x: pc.Dict(x.into(dict)).unwrap())
        {'a': 1, 'b': 2, 'c': 3}
        """
        from .._dict import Dict

        return Dict(dict(zip(keys, self.unwrap())))

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        >>> import pychain as pc
        >>> keys = [1, 2, 3]
        >>> values = ["a", "b", "c"]
        >>> pc.Iter(keys).with_values(values).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}

        This is equivalent to:
        >>> pc.Iter(keys).zip(values).pipe(lambda x: pc.Dict(x.into(dict)).unwrap())
        {1: 'a', 2: 'b', 3: 'c'}
        """
        from .._dict import Dict

        return Dict(dict(zip(self.unwrap(), values)))
