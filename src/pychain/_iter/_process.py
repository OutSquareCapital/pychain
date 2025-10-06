import itertools
from collections import deque
from collections.abc import Callable, Iterable
from random import Random
from typing import Any, Self

import cytoolz as cz

from .._core import CommonBase
from .._protocols import Peeked


class IterProcess[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def to_list(self) -> Self:
        """
        Transform the iterable into a list and return self.

            >>> from pychain import Iter
            >>> Iter((1, 2, 3)).to_list()
            [1, 2, 3]
        """
        return self._new(list(self._data))

    def to_deque(self, maxlen: int | None = None) -> Self:
        """
        Return an Iter wrapping the elements of the iterable.

            >>> from pychain import Iter
            >>> Iter((1, 2, 3)).to_deque()
            deque([1, 2, 3])
        """
        return self._new(deque(self._data, maxlen))

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

    def elements(self) -> Self:
        """
        Iterator over elements repeating each as many times as its count.

        >>> from pychain import Iter
        >>> Iter("ABCABC").elements().sort()
        ['A', 'A', 'B', 'B', 'C', 'C']

        Knuth's example for prime factors of 1836:  2**2 * 3**3 * 17**1

        >>> import math
        >>> Iter({2: 2, 3: 3, 17: 1}).elements().pipe_into(math.prod)
        1836

        Note, if an element's count has been set to zero or is a negative
        number, elements() will ignore it.

        """
        from collections import Counter

        return self._new(Counter(self._data).elements())

    def reverse(self) -> Self:
        """
        Return a new Iterable wrapper with elements in reverse order.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).reverse().to_list()
        [3, 2, 1]

        Note: This method must consume the entire iterable to perform the reversal.

        The result is a new iterable over the reversed sequence.
        """
        return self._new(reversed(list(self._data)))
