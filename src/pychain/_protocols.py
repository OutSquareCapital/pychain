from collections.abc import Iterable, Iterator
from typing import Any, NamedTuple, Protocol


class Peeked[T](NamedTuple):
    value: T | tuple[T, ...]
    sequence: Iterable[T]


class Pluckable[KT, VT](Protocol):
    def __getitem__(self, key: KT) -> VT: ...


class SupportsDunderLT[T](Protocol):
    def __lt__(self, other: T, /) -> bool: ...


class SupportsDunderGT[T](Protocol):
    def __gt__(self, other: T, /) -> bool: ...


class SupportsDunderLE[T](Protocol):
    def __le__(self, other: T, /) -> bool: ...


class SupportsDunderGE[T](Protocol):
    def __ge__(self, other: T, /) -> bool: ...


class SupportsAllComparisons(
    SupportsDunderLT[Any],
    SupportsDunderGT[Any],
    SupportsDunderLE[Any],
    SupportsDunderGE[Any],
    Protocol,
): ...


type SupportsRichComparison[T] = SupportsDunderLT[T] | SupportsDunderGT[T]


class NPTypeLike[T](Protocol): ...


class NPArrayLike[S, D: NPTypeLike[Any]](Protocol):
    """Array protocol to support numpy arrays and similar objects, without needing numpy as an explicit dependency."""

    def __iter__(self) -> Iterator[D]: ...
    def __array__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __array_finalize__(self, *args: Any, **kwargs: Any) -> None: ...
    def __array_wrap__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __getitem__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __setitem__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def shape(self) -> S: ...
    @property
    def dtype(self) -> Any: ...
    @property
    def ndim(self) -> int: ...
    @property
    def size(self) -> int: ...


type NDArray[T: NPTypeLike[Any]] = NPArrayLike[tuple[int, ...], T]
