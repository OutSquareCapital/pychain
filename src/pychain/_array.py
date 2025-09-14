from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._iter import Iter

type NumpyType = np.void | np.floating | np.integer | np.unsignedinteger | np.bool_


class Array[T: NumpyType](CommonBase[NDArray[T]]):
    __slots__ = "_data"
    _data: NDArray[T]

    def to_iter(self) -> "Iter[T]":
        return iter_factory(self._data)
