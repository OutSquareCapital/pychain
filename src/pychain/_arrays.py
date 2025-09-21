from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Concatenate

from ._core import CommonBase, iter_factory
from ._protocols import NDArray

if TYPE_CHECKING:
    from ._iter import Iter


class Array[T: NDArray[Any]](CommonBase[T]):
    """
    Wrapper for numpy arrays and similar objects.
    This is a simple class but that allows to use the same API as the other wrappers.
    It is mainly useful to chain operations on numpy arrays.
    """

    __slots__ = "_data"
    _data: T

    def pipe_into[**P, U: NDArray[Any]](
        self,
        func: Callable[
            Concatenate[T, P],
            U,
        ],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Array[U]":
        return Array(func(self._data, *args, **kwargs))

    def to_iter(self) -> Iter[T]:
        """
        Convert the wrapped array to an Iter wrapper.

            >>> import numpy as np
            >>> import pychain as pc
            >>>
            >>> data = np.array([1, 2, 3])
            >>>
            >>> pc.Array(data).to_iter().to_list()
            [np.int64(1), np.int64(2), np.int64(3)]
        """
        return iter_factory(self._data)
