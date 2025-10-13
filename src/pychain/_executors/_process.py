import itertools
from collections.abc import Callable, Iterable, Iterator
from functools import partial
from random import Random
from typing import Any, Self

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper, Peeked


class BaseProcess[T](IterWrapper[T]):
    def cycle(self) -> Self:
        """
        Repeat the sequence indefinitely.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

            >>> from pychain import Iter
            >>> Iter([1, 2]).cycle().head(5).into(list)
            [1, 2, 1, 2, 1]
        """
        return self._new(itertools.cycle)

    def interpose(self, element: T) -> Self:
        """
        Interpose element between items and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([1, 2]).interpose(0).into(list)
            [1, 0, 2]
        """
        return self._new(partial(cz.itertoolz.interpose, element))

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Randomly sample items with given probability.

            >>> from pychain import Iter
            >>> len(Iterable(Iter([1, 2, 3]).random_sample(0.5)))  # doctest: +SKIP
            1
        """

        return self._new(
            partial(cz.itertoolz.random_sample, probability, random_state=state)
        )

    def accumulate(self, func: Callable[[T, T], T]) -> Self:
        """
        Return cumulative application of binary op provided by the function.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).accumulate(lambda a, b: a + b).into(list)
            [1, 3, 6]
        """
        return self._new(partial(cz.itertoolz.accumulate, func))

    def insert_left(self, value: T) -> Self:
        """
        Prepend value to the sequence and return a new Iterable wrapper.

            >>> from pychain import Iter
            >>> Iter([2, 3]).insert_left(1).into(list)
            [1, 2, 3]
        """
        return self._new(partial(cz.itertoolz.cons, value))

    def peekn(self, n: int) -> Self:
        """¨
        Print and return sequence after peeking n items.

            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).peekn(2).into(list)
            Peeked 2 values: (1, 2)
            [1, 2, 3]
        """

        def _(data: Iterable[T]) -> Iterable[T]:
            peeked = Peeked(*cz.itertoolz.peekn(n, data))
            print(f"Peeked {n} values: {peeked.value}")
            return peeked.sequence

        return self._new(_)

    def peek(self) -> Self:
        """
        Print and return sequence after peeking first item.

            >>> from pychain import Iter
            >>> Iter([1, 2]).peek().into(list)
            Peeked value: 1
            [1, 2]
        """

        def _(data: Iterable[T]) -> Iterable[T]:
            peeked = Peeked(*cz.itertoolz.peek(data))
            print(f"Peeked value: {peeked.value}")
            return peeked.sequence

        return self._new(_)

    def merge_sorted(
        self, *others: Iterable[T], sort_on: Callable[[T], Any] | None = None
    ) -> Self:
        """
        Merge already-sorted sequences.

            >>> from pychain import Iter
            >>> Iter([1, 3]).merge_sorted([2, 4]).into(list)
            [1, 2, 3, 4]
        """
        return self._new(cz.itertoolz.merge_sorted, *others, key=sort_on)

    def interleave(self, *others: Iterable[T]) -> Self:
        """
        Interleave multiple sequences element-wise.

            >>> from pychain import Iter
            >>> Iter([1, 2]).interleave([3, 4]).into(list)
            [1, 3, 2, 4]
        """
        return self._new(lambda data: cz.itertoolz.interleave((data, *others)))

    def concat(self, *others: Iterable[T]) -> Self:
        """
        Concatenate zero or more iterables, any of which may be infinite.

        An infinite sequence will prevent the rest of the arguments from being included.

        We use chain.from_iterable rather than chain(*seqs) so that seqs can be a generator.

            >>> from pychain import Iter
            >>> Iter([1, 2]).concat([3, 4], [5]).into(list)
            [1, 2, 3, 4, 5]
        """

        return self._new(lambda data: itertools.chain.from_iterable((data, *others)))

    def elements(self) -> Self:
        """
        Iterator over elements repeating each as many times as its count.

        >>> from pychain import Iter
        >>> Iter("ABCABC").elements().sort()
        ['A', 'A', 'B', 'B', 'C', 'C']

        Knuth's example for prime factors of 1836:  2**2 * 3**3 * 17**1

        >>> import math
        >>> Iter({2: 2, 3: 3, 17: 1}).elements().into(math.prod)
        1836

        Note, if an element's count has been set to zero or is a negative
        number, elements() will ignore it.

        """
        from collections import Counter

        return self._new(lambda x: Counter(x).elements())

    def reverse(self) -> Self:
        """
        Return a new Iterable wrapper with elements in reverse order.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3]).reverse().into(list)
        [3, 2, 1]

        Note: This method must consume the entire iterable to perform the reversal.

        The result is a new iterable over the reversed sequence.
        """
        return self._new(lambda x: reversed(list(x)))

    def is_strictly_n(
        self,
        n: int,
        too_short: Callable[..., Iterator[T]] | None = None,
        too_long: Callable[..., Iterator[T]] | None = None,
    ) -> Self:
        """
        Validate that *iterable* has exactly *n* items and return them if it does.

        If it has fewer than *n* items, call function *too_short* with the actual number of items.

        If it has more than *n* items, call function *too_long* with the number ``n + 1``.

        >>> from pychain import Iter
        >>> iterable = ["a", "b", "c", "d"]
        >>> n = 4
        >>> Iter(iterable).is_strictly_n(n).into(list)
        ['a', 'b', 'c', 'd']

        Note that the returned iterable must be consumed in order for the check to
        be made.

        By default, *too_short* and *too_long* are functions that raise
        ``ValueError``.

        >>> Iter("ab").is_strictly_n(3).into(list)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: too few items in iterable (got 2)

        >>> Iter("abc").is_strictly_n(2).into(list)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ValueError: too many items in iterable (got at least 3)

        You can instead supply functions that do something else.

        *too_short* will be called with the number of items in *iterable*.

        *too_long* will be called with `n + 1`.

        >>> def too_short(item_count):
        ...     raise RuntimeError
        >>> Iter("abcd").is_strictly_n(6, too_short=too_short).into(list)
        Traceback (most recent call last):
        ...
        RuntimeError

        >>> def too_long(item_count):
        ...     print("The boss is going to hear about this")
        >>> Iter("abcdef").is_strictly_n(4, too_long=too_long).into(list)
        The boss is going to hear about this
        ['a', 'b', 'c', 'd']
        """
        return self._new(mit.strictly_n, n, too_short, too_long)
