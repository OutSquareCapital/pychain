from collections import deque
from collections.abc import Iterable
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import CommonBase, Transform, dict_factory, mut_seq_factory

if TYPE_CHECKING:
    from .._dict import Dict
    from .._sequence import SeqMut


class IterConvert[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def to_list(self) -> "SeqMut[T]":
        """Return a SeqMut wrapping the elements of the iterable.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).to_list()
            [1, 2, 3]
        """
        return mut_seq_factory(list(self._data))

    def to_deque(self, maxlen: int | None = None) -> "SeqMut[T]":
        """Return a SeqMut wrapping the elements of the iterable.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 2, 3]).to_deque()
            deque([1, 2, 3])
        """
        return mut_seq_factory(deque(self._data, maxlen))

    def group_by[K](self, on: Transform[T, K]) -> "Dict[K, list[T]]":
        """Group elements by key function and return a Dict result.

        **Example:**
            >>> from pychain import Iter
            >>> Iter(["a", "bb"]).group_by(len)
            {1: ['a'], 2: ['bb']}
        """
        return dict_factory(cz.itertoolz.groupby(on, self._data))

    def frequencies(self) -> "Dict[T, int]":
        """Return a Dict of value frequencies.

        **Example:**
            >>> from pychain import Iter
            >>> Iter([1, 1, 2]).frequencies()
            {1: 2, 2: 1}
        """
        return dict_factory(cz.itertoolz.frequencies(self._data))
