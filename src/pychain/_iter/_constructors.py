import itertools
from collections.abc import Callable
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import iter_factory

if TYPE_CHECKING:
    from ._main import Iter


class IterConstructors:
    @staticmethod
    def from_count(start: int = 0, step: int = 1) -> Iter[int]:
        """
        Create an infinite iterator of evenly spaced values.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> from pychain import Iter
        >>> Iter.from_count(10, 2).head(3).into(list)
        [10, 12, 14]
        """
        return iter_factory(itertools.count(start, step))

    @staticmethod
    def from_range(start: int, stop: int, step: int = 1) -> Iter[int]:
        """
        Create an iterator from a range.

        Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> from pychain import Iter
        >>> Iter.from_range(1, 5).into(list)
        [1, 2, 3, 4]
        """
        return iter_factory(range(start, stop, step))

    @staticmethod
    def from_func[T](func: Callable[[T], T], x: T) -> Iter[T]:
        """
        Create an infinite iterator by repeatedly applying a function into an original input x.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> from pychain import Iter
        >>> Iter.from_func(lambda x: x + 1, 0).head(3).into(list)
        [0, 1, 2]
        """
        return iter_factory(cz.itertoolz.iterate(func, x))

    @staticmethod
    def from_[T](*elements: T) -> Iter[T]:
        """
        Create an iterator from the given elements.

        >>> from pychain import Iter
        >>> Iter.from_(1, 2, 3).into(list)
        [1, 2, 3]
        """
        return iter_factory(elements)
