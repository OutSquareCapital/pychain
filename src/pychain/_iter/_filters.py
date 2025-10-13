from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Any

import more_itertools as mit

from .._core import CommonBase
from .._executors import BaseFilter

if TYPE_CHECKING:
    from ._main import Iter


class IterFilter[T](BaseFilter[T]):
    def filter_contain[U: CommonBase[Iterable[str]]](self: U, text: str) -> U:
        """
        Return elements that contain the given text.

            >>> from pychain import Iter
            >>> Iter(["apple", "banana", "cherry", "date"]).filter_contain("ana").into(
            ...     list
            ... )
            ['banana']
        """
        return self._new(lambda data: (x for x in data if text in x))

    def filter_subclass[U: Iterable[type], R](
        self: CommonBase[U], parent: type[R]
    ) -> Iter[type[R]]:
        """
        Return elements that are subclasses of the given class.

            >>> from pychain import Iter
            >>> class A:
            ...     pass
            >>> class B(A):
            ...     pass
            >>> class C:
            ...     pass
            >>> Iter([A, B, C]).filter_subclass(A).map(lambda c: c.__name__).into(list)
            ['A', 'B']
        """
        return self.pipe_into(lambda data: (x for x in data if issubclass(x, parent)))

    def filter_type[R](self, typ: type[R]) -> Iter[R]:
        """
        Return elements that are instances of the given type.

            >>> from pychain import Iter
            >>> Iter([1, "two", 3.0, "four", 5]).filter_type(int).into(list)
            [1, 5]
        """
        return self.pipe_into(lambda data: (x for x in data if isinstance(x, typ)))

    def filter_callable(self) -> Iter[Callable[..., Any]]:
        """
        Return only elements that are callable.

        >>> from pychain import Iter
        >>> Iter([len, 42, str, None, list]).filter_callable().into(list)
        [<built-in function len>, <class 'str'>, <class 'list'>]
        """
        return self.pipe_into(lambda data: (x for x in data if callable(x)))

    def filter_map[R](self, func: Callable[[T], R]) -> Iter[R]:
        """
        Apply func to every element of iterable, yielding only those which are not None.

        >>> from pychain import Iter
        >>> elems = ["1", "a", "2", "b", "3"]
        >>> Iter(elems).filter_map(lambda s: int(s) if s.isnumeric() else None).into(
        ...     list
        ... )
        [1, 2, 3]
        """
        return self.pipe_into(partial(mit.filter_map, func))
