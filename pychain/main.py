from collections.abc import Callable, Iterable
import cytoolz as cz
from dataclasses import dataclass

type AggFunc[T, V] = Callable[[Iterable[T]], V]


@dataclass(slots=True, frozen=True)
class Stream[T]:
    _data: Iterable[T]

    def _new[U](self, data: Iterable[U]) -> "Stream[U]":
        return self.__class__(data)  # type: ignore

    def map[U](self, f: Callable[[T], U]) -> "Stream[U]":
        """
        Make an iterator that computes the function using arguments from each of the iterables.

        Stops when the shortest iterable is exhausted."""
        return self._new(map(f, self._data))

    def filter(self, f: Callable[[T], bool]) -> "Stream[T]":
        """
        Return an iterator yielding those items of iterable for which function(item) is true.

        If function is None, return the items that are true.
        """
        return self._new(data=filter(f, self._data))

    def flat_map[U](self, f: Callable[[T], Iterable[U]]) -> "Stream[U]":
        """
        *Copied from toolz documentation*.

        Concatenate zero or more iterables, any of which may be infinite.

        An infinite sequence will prevent the rest of the arguments from
        being included.

        We use chain.from_iterable rather than ``chain(*seqs)`` so that seqs
        can be a generator.

        >>> list(concat([[], [1], [2, 3]]))
        [1, 2, 3]

        See also:
            itertools.chain.from_iterable  equivalent
        """
        return self._new(cz.itertoolz.concat(map(f, self._data)))

    def to_list(self) -> list[T]:
        return list(self._data)
