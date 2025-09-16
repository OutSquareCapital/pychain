from collections.abc import Callable, Iterable, MutableSequence, Sequence
from typing import TYPE_CHECKING, Concatenate, Self

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._iter import Iter


class Seq[T](CommonBase[Sequence[T]]):
    _data: Sequence[T]
    __slots__ = ("_data",)

    def pipe_unwrap[**P, U](
        self,
        func: Callable[Concatenate[Sequence[T], P], Sequence[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Seq[U]":
        return Seq(func(self._data, *args, **kwargs))

    def to_iter(self) -> "Iter[T]":
        """Return an iterator over the sequence elements."""
        return iter_factory(iter(self._data))

    def count(self, value: T) -> int:
        """
        Count occurrences of value in the sequence.

            >>> Seq([1, 2, 1]).count(1)
            2
        """
        return self._data.count(value)

    def index(self, value: T, start: int = 0, stop: int | None = None) -> int:
        """
        Return the index of the first occurrence of value in the sequence.

            >>> Seq([1, 2, 1]).index(1)
            0
        """
        if stop is not None:
            return self._data.index(value, start, stop)
        return self._data.index(value, start)


class SeqMut[T](Seq[T]):
    _data: MutableSequence[T]
    __slots__ = ("_data",)  # type: ignore

    def pipe[**P, U](
        self,
        func: Callable[Concatenate[MutableSequence[T], P], MutableSequence[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "SeqMut[U]":
        return SeqMut(func(self._data, *args, **kwargs))

    def clear(self) -> Self:
        """
        Clear the sequence and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).clear()
            []
        """
        self._data.clear()
        return self

    def insert(self, index: int, value: T) -> Self:
        """
        Insert an object into the sequence at the specified index and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).insert(1, 3)
            [1, 3, 2]
        """
        self._data.insert(index, value)
        return self

    def append(self, value: T) -> Self:
        """
        Append object to the end of the sequence and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).append(3)
            [1, 2, 3]
        """
        self._data.append(value)
        return self

    def extend(self, *others: Iterable[T]) -> Self:
        """
        Extend the sequence with elements from another iterable and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).extend([3, 4])
            [1, 2, 3, 4]
        """
        self._data.extend(*others)
        return self

    def remove(self, value: T) -> Self:
        """
        Remove an object from the sequence and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).remove(2)
            [1]
        """
        self._data.remove(value)
        return self

    def reverse(self) -> Self:
        """
        Reverse the order of the sequence and return self for convenience.
        **Warning**: Mutates the original sequence.

            >>> SeqMut([1, 2]).reverse()
            [2, 1]
        """
        self._data.reverse()
        return self
