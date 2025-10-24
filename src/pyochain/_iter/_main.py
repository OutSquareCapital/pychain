from __future__ import annotations

from collections.abc import Callable, Collection, Generator, Iterable, Iterator
from typing import Any, Concatenate

from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._constructors import IterConstructors
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
        return self.into(Iter.from_)
