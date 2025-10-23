from collections.abc import Iterable, Iterator, Sized
from typing import NamedTuple, Protocol


class Peeked[T](NamedTuple):
    value: T | tuple[T, ...]
    sequence: Iterator[T]


class SupportsDunderLT[T](Protocol):
    def __lt__(self, other: T, /) -> bool: ...


class SupportsDunderGT[T](Protocol):
    def __gt__(self, other: T, /) -> bool: ...


class SupportsDunderLE[T](Protocol):
    def __le__(self, other: T, /) -> bool: ...


class SupportsDunderGE[T](Protocol):
    def __ge__(self, other: T, /) -> bool: ...


class SupportsKeysAndGetItem[K, V](Protocol):
    def keys(self) -> Iterable[K]: ...
    def __getitem__(self, key: K, /) -> V: ...


class SupportsAllComparisons[T](
    SupportsDunderLT[T],
    SupportsDunderGT[T],
    SupportsDunderLE[T],
    SupportsDunderGE[T],
    Protocol,
): ...


type SupportsRichComparison[T] = SupportsDunderLT[T] | SupportsDunderGT[T]


class SizedIterable[T](Sized, Iterable[T]): ...
