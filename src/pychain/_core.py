from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, Self

import cytoolz as cz

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter
    from ._list import List


type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]


def peekn[T](seq: Iterable[T], n: int, note: str | None = None):
    values, sequence = cz.itertoolz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def peek[T](seq: Iterable[T], note: str | None = None):
    value, sequence = cz.itertoolz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


class CommonBase[T](ABC):
    __slots__ = ("_data",)

    def __init__(self, data: T) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"{self._data.__repr__()}"

    def _new(self, data: T) -> Self:
        return self.__class__(data)

    def unwrap(self) -> T:
        """Return the underlying data."""
        return self._data

    @abstractmethod
    def transform[**P](
        self,
        func: Callable[Concatenate[T, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        raise NotImplementedError

    def into[U, **P](
        self,
        func: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Applies a function to the underlying data to terminate the chain.

        This method "unwraps" the data and passes it to the given function,
        returning the raw result.

        It is used as a final step to get a
        computed value out of the chain.

        Example:
            >>> from ._list import List
            >>> List([1, 2, 3, 4]).into(sum)
            10
        """
        return func(self._data, *args, **kwargs)

    def pipe(self, *funcs: Process[T]) -> Self:
        """Passes the underlying data through one or more functions in a sequence.

        This allows you to insert a regular function that is not a method of
        the class into a call chain. The underlying data is passed as the
        first argument to the first function.

        It is equivalent to the `pipe operator` (`|>`) found in other languages.

        Example:
            >>>
            >>> from ._array import Array
            >>> import numpy as np
            >>> Array(np.array([1, 2, 3])).pipe(
            ...     lambda x: x.clip(0, 2), lambda x: x * 2
            ... ).unwrap()
            array([2, 4, 4])
        """

        return self._new(cz.functoolz.pipe(self._data, *funcs))


def iter_on[T](data: Iterable[T]) -> "Iter[T]":
    from ._iter import Iter

    return Iter(data)


def dict_on[K, V](data: dict[K, V]) -> "Dict[K, V]":
    from ._dict import Dict

    return Dict(data)


def list_on[T](data: list[T]) -> "List[T]":
    from ._list import List

    return List(data)
