import itertools
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import reduce
from random import Random
from typing import Any, Concatenate, Self

import cytoolz as cz

from ._core import Check, Process, peek, peekn, tap


@dataclass(slots=True)
class BaseIter[T]:
    _data: Iterable[T]
    """
    Base wrapper for Iterable-like eager transformations. Use Iter for public API.
    """

    def compose(self, *funcs: Process[Iterable[T]]) -> Self:
        """Compose functions and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1]).compose(lambda l: l).into_list().unwrap()
            [1]
        """
        return self.__class__(cz.functoolz.pipe(self._data, *funcs))

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """Filter elements according to func and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).into_list().unwrap()
            [2, 3]
        """
        return self.__class__(filter(func, self._data, *args, **kwargs))

    def flatten(self) -> Self:
        """Flatten one level of nesting and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([[1, 2], [3]]).flatten().into_list().unwrap()
            [1, 2, 3]
        """
        return self.__class__(cz.itertoolz.concat(self._data))

    def take_while(self, predicate: Check[T]) -> Self:
        """Take items while predicate holds and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).into_list().unwrap()
            [1, 2]
        """
        return self.__class__(itertools.takewhile(predicate, self._data))

    def drop_while(self, predicate: Check[T]) -> Self:
        """Drop items while predicate holds and return the remainder.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).into_list().unwrap()
            [0]
        """
        return self.__class__(itertools.dropwhile(predicate, self._data))

    def interpose(self, element: T) -> Self:
        """Interpose element between items and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).interpose(0).into_list().unwrap()
            [1, 0, 2]
        """
        return self.__class__(cz.itertoolz.interpose(element, self._data))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """Return the top-n items according to key.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 3, 2]).top_n(2).into_list().unwrap()
            [3, 2]
        """
        return self.__class__(cz.itertoolz.topk(n, self._data, key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """Randomly sample items with given probability.

        Example:
            >>> from ._lib import Iter
            >>> len(Iterable(Iter([1, 2, 3]).random_sample(0.5)))  # doctest: +SKIP
            1
        """
        return self.__class__(
            cz.itertoolz.random_sample(probability, self._data, state)
        )

    def accumulate(self, f: Callable[[T, T], T]) -> Self:
        """Return cumulative application of binary op f.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).accumulate(lambda a, b: a + b).into_list().unwrap()
            [1, 3, 6]
        """
        return self.__class__(cz.itertoolz.accumulate(f, self._data))

    def insert_left(self, value: T) -> Self:
        """Prepend value to the sequence and return a new Iterable wrapper.

        Example:
            >>> from ._lib import Iter
            >>> Iter([2, 3]).insert_left(1).into_list().unwrap()
            [1, 2, 3]
        """
        return self.__class__(cz.itertoolz.cons(value, self._data))

    def peekn(self, n: int, note: str | None = None) -> Self:
        """Print and return sequence after peeking n items.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).peekn(2).into_list().unwrap()
            Peeked 2 values: [1, 2]
            [1, 2, 3]
        """
        return self.__class__(peekn(self._data, n, note))

    def peek(self, note: str | None = None) -> Self:
        """Print and return sequence after peeking first item.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).peek().into_list().unwrap()
            Peeked value: 1
            [1, 2]
        """
        return self.__class__(peek(self._data, note))

    def head(self, n: int) -> Self:
        """Return first n elements wrapped.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).head(2).into_list().unwrap()
            [1, 2]
        """
        return self.__class__(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        """Return last n elements wrapped.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).tail(2).into_list().unwrap()
            [2, 3]
        """
        return self.__class__(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        """Drop first n elements and return the remainder wrapped.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).drop_first(1).into_list().unwrap()
            [2, 3]
        """
        return self.__class__(cz.itertoolz.drop(n, self._data))

    def every(self, index: int) -> Self:
        """Return every nth item starting from first.

        Example:
            >>> from ._lib import Iter
            >>> Iter([10, 20, 30, 40]).every(2).into_list().unwrap()
            [10, 30]
        """
        return self.__class__(cz.itertoolz.take_nth(index, self._data))

    def unique(self) -> Self:
        """Return unique items preserving order.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 1]).unique().into_list().unwrap()
            [1, 2]
        """
        return self.__class__(cz.itertoolz.unique(self._data))

    def tap(self, func: Callable[[T], None]) -> Self:
        """Call func on each item and return the original sequence wrapped.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).tap(lambda x: None).into_list().unwrap()
            [1, 2]
        """
        return self.__class__(tap(self._data, func))

    def merge_sorted(
        self, *others: Iterable[T], sort_on: Callable[[T], Any] | None = None
    ) -> Self:
        """Merge already-sorted sequences.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 3]).merge_sorted([2, 4]).into_list().unwrap()
            [1, 2, 3, 4]
        """
        return self.__class__(
            cz.itertoolz.merge_sorted(self._data, *others, key=sort_on)
        )

    def interleave(self, *others: Iterable[T]) -> Self:
        """Interleave multiple sequences element-wise.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).interleave([3, 4]).into_list().unwrap()
            [1, 3, 2, 4]
        """
        return self.__class__(cz.itertoolz.interleave((self._data, *others)))

    def concat(self, *others: Iterable[T]) -> Self:
        """Concatenate multiple sequences.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1]).concat([2, 3]).into_list().unwrap()
            [1, 2, 3]
        """
        return self.__class__(cz.itertoolz.concat((self._data, *others)))

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce the sequence using func.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2, 3]).reduce(lambda a, b: a + b)
            6
        """
        return reduce(func, self._data)

    def is_distinct(self) -> bool:
        """Return True if all items are distinct.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).is_distinct()
            True
        """
        return cz.itertoolz.isdistinct(self._data)

    def all(self) -> bool:
        """Return True if all items are truthy.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, True]).all()
            True
        """
        return all(self._data)

    def any(self) -> bool:
        """Return True if any item is truthy.

        Example:
            >>> from ._lib import Iter
            >>> Iter([0, 1]).any()
            True
        """
        return any(self._data)

    def agg[**P](
        self,
        f: Callable[Concatenate[Iterable[T], P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Apply aggregator f to the whole Iterable and return result.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).agg(sum)
            3
        """
        return f(self._data, *args, **kwargs)

    def first(self) -> T:
        """Return the first element.

        Example:
            >>> from ._lib import Iter
            >>> Iter([9]).first()
            9
        """
        return cz.itertoolz.first(self._data)

    def second(self) -> T:
        """Return the second element.

        Example:
            >>> from ._lib import Iter
            >>> Iter([9, 8]).second()
            8
        """
        return cz.itertoolz.second(self._data)

    def last(self) -> T:
        """Return the last element.

        Example:
            >>> from ._lib import Iter
            >>> Iter([7, 8, 9]).last()
            9
        """
        return cz.itertoolz.last(self._data)

    def length(self) -> int:
        """Return the length of the sequence.

        Example:
            >>> from ._lib import Iter
            >>> Iter([1, 2]).length()
            2
        """
        return cz.itertoolz.count(self._data)

    def at_index(self, index: int) -> T:
        """Return item at index.

        Example:
            >>> from ._lib import Iter
            >>> Iter([10, 20]).at_index(1)
            20
        """
        return cz.itertoolz.nth(index, self._data)
