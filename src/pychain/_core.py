from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, MutableSequence, Sequence
from typing import TYPE_CHECKING, Any, Concatenate, NamedTuple, Protocol, Self

import cytoolz as cz

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter
    from ._sequence import Seq, SeqMut


type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]


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

    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)

    @abstractmethod
    def pipe_unwrap[**P](
        self,
        func: Callable[Concatenate[Self, P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        """Pipe underlying data in the function and return a new wrapped instance."""
        raise NotImplementedError

    def pipe_chain(self, *funcs: Process[T]) -> Self:
        """Pipe a value through a sequence of functions.

        Prefer this method over multiple pipe_unwrap calls when the functions don't transform the type.

        I.e. Iter(data).pipe_chain(f, g, h).unwrap() is equivalent to h(g(f(data)))
        """
        return self._new(cz.functoolz.pipe(self._data, *funcs))


def iter_factory[T](data: Iterable[T]) -> "Iter[T]":
    from ._iter import Iter

    return Iter(data)


def dict_factory[K, V](data: dict[K, V]) -> "Dict[K, V]":
    from ._dict import Dict

    return Dict(data)


def mut_seq_factory[T](data: MutableSequence[T]) -> "SeqMut[T]":
    from ._sequence import SeqMut

    return SeqMut(data)


def seq_factory[T](data: Sequence[T]) -> "Seq[T]":
    from ._sequence import Seq

    return Seq(data)
