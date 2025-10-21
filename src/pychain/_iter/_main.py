from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any, Concatenate

from .._core import SupportsRichComparison
from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._constructors import IterConstructors
from ._filters import BaseFilter
from ._groups import BaseGroups
from ._joins import BaseJoins
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
    BaseJoins[T],
    BaseGroups[T],
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
        return self.apply(
            lambda data: map(lambda x: func(Iter(x), *args, **kwargs), data)
        )

    def struct[**P, R, K, V](
        self: Iter[dict[K, V]],
        func: Callable[Concatenate[Dict[K, V], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to each element after wrapping it in a Dict.

        This is a convenience method for the common pattern of mapping a function over an iterable of dictionaries.
        >>> from typing import Any
        >>> import pychain as pc

        >>> data: list[dict[str, Any]] = [
        ...     {"name": "Alice", "age": 30, "city": "New York"},
        ...     {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ...     {"name": "Charlie", "age": 35, "city": "New York"},
        ...     {"name": "David", "age": 40, "city": "Paris"},
        ... ]
        >>>
        >>> def to_title(d: pc.Dict[str, Any]) -> pc.Dict[str, Any]:
        ...     return d.map_keys(lambda k: k.title())
        >>> def is_young(d: pc.Dict[str, Any]) -> bool:
        ...     return d.unwrap().get("Age", 0) < 30
        >>> def set_continent(d: pc.Dict[str, Any], value: str) -> dict[str, Any]:
        ...     return d.with_key("Continent", value).unwrap()
        >>>
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
        ... )  # doctest: +NORMALIZE_WHITESPACE
        Dict({
        'America': [
            {'Name': 'Alice', 'City': 'New York'},
            {'Name': 'Charlie', 'City': 'New York'}
        ],
        'Europe': [
            {'Name': 'David', 'City': 'Paris'}
        ]
        })
        """
        from .._dict import Dict

        return self.apply(
            lambda data: map(lambda x: func(Dict(x), *args, **kwargs), data)
        )

    def sort[U: SupportsRichComparison[Any]](
        self: Iter[U], reverse: bool = False
    ) -> Iter[U]:
        """
        Sort the elements of the sequence.
        Note: This method must consume the entire iterable to perform the sort.

        The result is a new iterable over the sorted sequence.

        >>> import pychain as pc
        >>> pc.Iter([3, 1, 2]).sort().into(list)
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
