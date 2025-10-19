from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import TYPE_CHECKING

import cytoolz as cz

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

        >>> import pychain as pc
        >>> pc.Iter.from_count(10, 2).head(3).into(list)
        [10, 12, 14]
        """
        from ._main import Iter

        return Iter(itertools.count(start, step))

    @staticmethod
    def from_range(start: int, stop: int, step: int = 1) -> Iter[int]:
        """
        Create an iterator from a range.

        Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> import pychain as pc
        >>> pc.Iter.from_range(1, 5).into(list)
        [1, 2, 3, 4]
        """
        from ._main import Iter

        return Iter(range(start, stop, step))

    @staticmethod
    def from_func[U](func: Callable[[U], U], x: U) -> Iter[U]:
        """
        Create an infinite iterator by repeatedly applying a function into an original input x.

        **Warning** ⚠️

        This creates an infinite iterator.

        Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> import pychain as pc
        >>> pc.Iter.from_func(lambda x: x + 1, 0).head(3).into(list)
        [0, 1, 2]
        """
        from ._main import Iter

        return Iter(cz.itertoolz.iterate(func, x))

    @staticmethod
    def from_[U](*elements: U) -> Iter[U]:
        """
        Create an iterator from the given elements.

        >>> import pychain as pc
        >>> pc.Iter.from_(1, 2, 3).into(list)
        [1, 2, 3]
        """
        from ._main import Iter

        return Iter(elements)
