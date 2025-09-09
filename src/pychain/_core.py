from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self

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


class CommonBase[T]:
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

    def into[U, **P](
        self,
        func: Callable[Concatenate[Self, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        return func(self, *args, **kwargs)

    def pipe(self, *funcs: Process[Self]) -> Self:
        return self._new(cz.functoolz.pipe(*funcs))


def iter_on[T](data: Iterable[T]) -> "Iter[T]":
    from ._iter import Iter

    return Iter(data)


def dict_on[K, V](data: dict[K, V]) -> "Dict[K, V]":
    from ._dict import Dict

    return Dict(data)


def list_on[T](data: list[T]) -> "List[T]":
    from ._list import List

    return List(data)
