from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate, NamedTuple, Protocol, Self

import cytoolz as cz

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter
    from ._list import List


type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]


class Peeked[T](NamedTuple):
    value: T | tuple[T, ...]
    sequence: Iterable[T]


class Pluckable[KT, VT](Protocol):
    def __getitem__(self, key: KT) -> VT: ...


class CommonBase[T](ABC):
    __slots__ = ("_data",)

    def __init__(self, data: T) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"{self._data.__repr__()}"

    def println(self) -> Self:
        print(self)
        return self

    def _new(self, data: T) -> Self:
        return self.__class__(data)

    def unwrap(self) -> T:
        """Return the underlying data."""
        return self._data

    @abstractmethod
    def into[**P](
        self,
        func: Callable[Concatenate[T, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        raise NotImplementedError

    def pipe(self, *funcs: Process[T]) -> Self:
        """Passes the underlying data through one or more functions in a sequence.

        This allows you to insert a regular function that is not a method of
        the class into a call chain. The underlying data is passed as the
        first argument to the first function.

        It is equivalent to the `pipe operator` (`|>`) found in other languages.

        **Example:**
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
