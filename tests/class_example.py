from collections.abc import Callable
from typing import Concatenate

import numpy as np
from numpy.typing import NDArray

import pychain as pc

type NumpyType = np.void | np.floating | np.integer | np.unsignedinteger | np.bool_


class Array[T: NumpyType](pc.CommonBase[NDArray[T]]):
    __slots__ = "_data"
    _data: NDArray[T]

    def pipe_unwrap[**P, U: NumpyType](
        self,
        func: Callable[Concatenate[NDArray[T], P], NDArray[U]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Array[U]":
        return Array(func(self._data, *args, **kwargs))

    def to_iter(self) -> pc.Iter[T]:
        return pc.Iter(self._data)


def check_array():
    data = pc.Iter.from_range(1, 10).unwrap()
    Array(np.array(data)).pipe_chain(
        lambda x: x + 2, lambda x: x * 3
    ).println().pipe_unwrap(lambda x: x.clip(10, 20))


if __name__ == "__main__":
    check_array()
