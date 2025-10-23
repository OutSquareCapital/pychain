from __future__ import annotations

from collections.abc import Callable, Collection, Generator, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Concatenate

from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._constructors import IterConstructors
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
    BaseJoins[T],
    BaseGroups[T],
    BaseEager[T],
    IterConstructors,
):
    """
    A wrapper around Python's built-in iterable types, providing a rich set of functional programming tools.

    It supports lazy evaluation, allowing for efficient processing of large datasets.

    It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

    It can be constructed from any iterable, including `lists`, `tuples`, `sets`, and `generators`.
    """

    __slots__ = ("_data",)

    def __init__(self, data: Iterator[T] | Generator[T, Any, Any]) -> None:
        self._data = data

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
            return (func(Iter.from_(x), *args, **kwargs) for x in data)

        return self.apply(_itr)

    def struct[**P, R, K, V](
        self: Iter[dict[K, V]],
        func: Callable[Concatenate[Dict[K, V], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to each element after wrapping it in a Dict.

        This is a convenience method for the common pattern of mapping a function over an iterable of dictionaries.
        Args:
            func: Function to apply to each wrapped dictionary.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        Example:
        ```python
        >>> from typing import Any
        >>> import pyochain as pc

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
        >>> pc.Iter.from_(data).struct(to_title).filter_false(is_young).map(
        ...     lambda d: d.drop("Age").with_key("Continent", "NA")
        ... ).map_if(
        ...     lambda d: d.unwrap().get("City") == "Paris",
        ...     lambda d: set_continent(d, "Europe"),
        ...     lambda d: set_continent(d, "America"),
        ... ).group_by(lambda d: d.get("Continent")).map_values(
        ...     lambda d: pc.Iter.from_(d)
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

        ```
        """
        from .._dict import Dict

        def _struct(data: Iterable[dict[K, V]]) -> Generator[R, None, None]:
            return (func(Dict(x), *args, **kwargs) for x in data)

        return self.apply(_struct)

    def with_keys[K](self, keys: Iterable[K]) -> Dict[K, T]:
        """
        Create a Dict by zipping the iterable with keys.

        Args:
            keys: Iterable of keys to pair with the values.
        Example:
        ```python
        >>> import pyochain as pc
        >>> keys = ["a", "b", "c"]
        >>> values = [1, 2, 3]
        >>> pc.Iter.from_(values).with_keys(keys).unwrap()
        {'a': 1, 'b': 2, 'c': 3}
        >>> # This is equivalent to:
        >>> pc.Iter.from_(keys).zip(values).pipe(
        ...     lambda x: pc.Dict(x.into(dict)).unwrap()
        ... )
        {'a': 1, 'b': 2, 'c': 3}

        ```
        """
        from .._dict import Dict

        return Dict(dict(zip(keys, self.unwrap())))

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        Args:
            values: Iterable of values to pair with the keys.
        Example:
        ```python
        >>> import pyochain as pc
        >>> keys = [1, 2, 3]
        >>> values = ["a", "b", "c"]
        >>> pc.Iter.from_(keys).with_values(values).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}
        >>> # This is equivalent to:
        >>> pc.Iter.from_(keys).zip(values).pipe(
        ...     lambda x: pc.Dict(x.into(dict)).unwrap()
        ... )
        {1: 'a', 2: 'b', 3: 'c'}

        ```
        """
        from .._dict import Dict

        return Dict(dict(zip(self.unwrap(), values)))


class Seq[T](BaseAgg[T], BaseEager[T]):
    """
    pyochain.Seq represent an in memory collection.

    Provides a subset of pyochain.Iter methods with eager evaluation, and is the return type of pyochain.Iter.collect().
    """

    __slots__ = ("_data",)

    def __init__(self, data: Collection[T]) -> None:
        self._data = data

    def iter(self) -> Iter[T]:
        """
        Get an iterator over the sequence.
        Call this to switch to lazy evaluation.
        """
        return Iter.from_(self.unwrap())
