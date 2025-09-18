import itertools
from collections import deque
from collections.abc import Callable, Iterable
from random import Random
from typing import Any, Concatenate, Self

import cytoolz as cz
import more_itertools as mit

from .._core import CommonBase
from .._protocols import Peeked


class IterProcess[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def to_list(self) -> Self:
        """
        Transform the iterable into a list and return self.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).to_list()
            [1, 2, 3]
        """
        return self._new(list(self._data))

    def to_deque(self, maxlen: int | None = None) -> Self:
        """
        Return an Iter wrapping the elements of the iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).to_deque()
            deque([1, 2, 3])
        """
        return self._new(deque(self._data, maxlen))

    def slice(self, start: int | None = None, stop: int | None = None) -> Self:
        """
        Return a slice of the iterable.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3, 4, 5]).slice(1, 4).to_list()
            [2, 3, 4]
        """
        return self._new(itertools.islice(self._data, start, stop))

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """
        Filter elements according to func and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter(lambda x: x > 1).to_list()
            [2, 3]
        """
        return self._new(filter(func, self._data, *args, **kwargs))

    def filter_false[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ) -> Self:
        """
        Return elements for which func is false.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).filter_false(lambda x: x > 1).to_list()
            [1]
        """
        return self._new(itertools.filterfalse(func, self._data, *args, **kwargs))

    def filter_except(
        self, func: Callable[[T], object], *exceptions: type[BaseException]
    ) -> Self:
        """
        Yield the items from iterable for which the validator function does not raise one of the specified exceptions.

        Validator is called for each item in iterable.

        It should be a function that accepts one argument and raises an exception if that item is not valid.

        If an exception other than one given by exceptions is raised by validator, it is raised like normal.

            >>> from pychain import Iter
            >>> iterable = ["1", "2", "three", "4", None]
            >>> Iter(iterable).filter_except(int, ValueError, TypeError).to_list()
            ['1', '2', '4']
        """
        return self._new(mit.filter_except(func, self._data, *exceptions))

    def compress(self, *selectors: bool) -> Self:
        """
        Filter elements using a boolean selector iterable.

            >>> from pychain import Iter
            >>> Iter("ABCDEF").compress(1, 0, 1, 0, 1, 1).to_list()
            ['A', 'C', 'E', 'F']
        """
        return self._new(itertools.compress(self._data, selectors))

    def take_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Take items while predicate holds and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).take_while(lambda x: x > 0).to_list()
            [1, 2]
        """
        return self._new(itertools.takewhile(predicate, self._data))

    def drop_while(self, predicate: Callable[[T], bool]) -> Self:
        """
        Drop items while predicate holds and return the remainder.

            >>> from pychain import Iter
            >>> Iter([1, 2, 0]).drop_while(lambda x: x > 0).to_list()
            [0]
        """
        return self._new(itertools.dropwhile(predicate, self._data))

    def cycle(self) -> Self:
        """
        Repeat the sequence indefinitely.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

            >>> from pychain import Iter
            >>> Iter([1, 2]).cycle().head(5).to_list()
            [1, 2, 1, 2, 1]
        """
        return self._new(itertools.cycle(self._data))

    def interpose(self, element: T) -> Self:
        """
        Interpose element between items and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2]).interpose(0).to_list()
            [1, 0, 2]
        """
        return self._new(cz.itertoolz.interpose(element, self._data))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None) -> Self:
        """
        Return the top-n items according to key.

            >>> from pychain import Iter
            >>> Iter([1, 3, 2]).top_n(2).to_list()
            [3, 2]
        """
        return self._new(cz.itertoolz.topk(n, self._data, key))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly sample items with given probability.

            >>> from pychain import Iter
            >>> len(Iterable(Iter([1, 2, 3]).random_sample(0.5)))  # doctest: +SKIP
            1
        """
        return self._new(cz.itertoolz.random_sample(probability, self._data, state))

    def accumulate(self, func: Callable[[T, T], T]) -> Self:
        """
        Return cumulative application of binary op provided by the function.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).accumulate(lambda a, b: a + b).to_list()
            [1, 3, 6]
        """
        return self._new(cz.itertoolz.accumulate(func, self._data))

    def insert_left(self, value: T) -> Self:
        """
        Prepend value to the sequence and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([2, 3]).insert_left(1).to_list()
            [1, 2, 3]
        """
        return self._new(cz.itertoolz.cons(value, self._data))

    def peekn(self, n: int) -> Self:
        """¨
        Print and return sequence after peeking n items.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).peekn(2).to_list()
            Peeked 2 values: (1, 2)
            [1, 2, 3]
        """

        def _():
            peeked = Peeked(*cz.itertoolz.peekn(n, self._data))
            print(f"Peeked {n} values: {peeked.value}")
            return peeked.sequence

        return self._new(_())

    def peek(self) -> Self:
        """
        Print and return sequence after peeking first item.

            >>> from pychain import Iter
            >>> Iter([1, 2]).peek().to_list()
            Peeked value: 1
            [1, 2]
        """

        def _():
            peeked = Peeked(*cz.itertoolz.peek(self._data))
            print(f"Peeked value: {peeked.value}")
            return peeked.sequence

        return self._new(_())

    def head(self, n: int) -> Self:
        """
        Return first n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).head(2).to_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.take(n, self._data))

    def tail(self, n: int) -> Self:
        """
        Return last n elements wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).tail(2).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.tail(n, self._data))

    def drop_first(self, n: int) -> Self:
        """
        Drop first n elements and return the remainder wrapped.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).drop_first(1).to_list()
            [2, 3]
        """
        return self._new(cz.itertoolz.drop(n, self._data))

    def every(self, index: int) -> Self:
        """
        Return every nth item starting from first.

            >>> from pychain import Iter
            >>> Iter([10, 20, 30, 40]).every(2).to_list()
            [10, 30]
        """
        return self._new(cz.itertoolz.take_nth(index, self._data))

    def unique(self) -> Self:
        """
        Return unique items preserving order.

            >>> from pychain import Iter
            >>> Iter([1, 2, 1]).unique().to_list()
            [1, 2]
        """
        return self._new(cz.itertoolz.unique(self._data))

    def merge_sorted(
        self, *others: Iterable[T], sort_on: Callable[[T], Any] | None = None
    ) -> Self:
        """
        Merge already-sorted sequences.

            >>> from pychain import Iter
            >>> Iter([1, 3]).merge_sorted([2, 4]).to_list()
            [1, 2, 3, 4]
        """
        return self._new(cz.itertoolz.merge_sorted(self._data, *others, key=sort_on))

    def interleave(self, *others: Iterable[T]) -> Self:
        """
        Interleave multiple sequences element-wise.

            >>> from pychain import Iter
            >>> Iter([1, 2]).interleave([3, 4]).to_list()
            [1, 3, 2, 4]
        """
        return self._new(cz.itertoolz.interleave((self._data, *others)))

    def concat(self, *others: Iterable[T]) -> Self:
        """
        Concatenate zero or more iterables, any of which may be infinite.
        An infinite sequence will prevent the rest of the arguments from being included.
        We use chain.from_iterable rather than chain(*seqs) so that seqs can be a generator.

            >>> from pychain import Iter
            >>> Iter([1, 2]).concat([3, 4], [5]).to_list()
            [1, 2, 3, 4, 5]
        """
        return self._new(itertools.chain.from_iterable((self._data, *others)))
