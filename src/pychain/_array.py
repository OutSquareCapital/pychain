from collections.abc import Callable
from typing import TYPE_CHECKING, Concatenate

import numpy as np
from numpy.typing import NDArray

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._iter import Iter

type NumpyType = np.void | np.floating | np.integer | np.unsignedinteger | np.bool_


class Array[T: NumpyType](CommonBase[NDArray[T]]):
    __slots__ = "_data"
    _data: NDArray[T]

    def pipe[**P, U: NumpyType](
        self,
        func: Callable[Concatenate[NDArray[T], P], NDArray[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Array[U]":
        return Array(func(self._data, *args, **kwargs))

    def to_iter(self) -> "Iter[T]":
        return iter_factory(self._data)
