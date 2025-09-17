import itertools
from collections.abc import Callable

import cytoolz as cz

from ._iter import Iter


def iter_count(start: int = 0, step: int = 1) -> Iter[int]:
    """
    Create an infinite iterator of evenly spaced values.

    **Warning** ⚠️

    This creates an infinite iterator.

    Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> iter_count(10, 2).head(3).to_list()
        [10, 12, 14]
    """
    return Iter(itertools.count(start, step))


def iter_range(start: int, stop: int, step: int = 1) -> Iter[int]:
    """
    Create an iterator from a range.

    Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> iter_range(1, 5).to_list()
        [1, 2, 3, 4]
    """
    return Iter(range(start, stop, step))


def iter_func[T](func: Callable[[T], T], x: T) -> Iter[T]:
    """
    Create an infinite iterator by repeatedly applying a function into an original input x.

    **Warning** ⚠️

    This creates an infinite iterator.

    Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> iter_func(lambda x: x + 1, 0).head(3).to_list()
        [0, 1, 2]
    """
    return Iter(cz.itertoolz.iterate(func, x))


def iter_on[T](*elements: T) -> Iter[T]:
    """
    Create an iterator from the given elements.

        >>> iter_on(1, 2, 3).to_list()
        [1, 2, 3]
    """
    return Iter(elements)
