from collections.abc import Iterable
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


class SupportsKeysAndGetItem[K, V](Protocol):
    def keys(self) -> Iterable[K]: ...
    def __getitem__(self, key: K, /) -> V: ...


class SupportsAllComparisons(
    SupportsDunderLT[Any],
    SupportsDunderGT[Any],
    SupportsDunderLE[Any],
    SupportsDunderGE[Any],
    Protocol,
): ...


type SupportsRichComparison[T] = SupportsDunderLT[T] | SupportsDunderGT[T]
