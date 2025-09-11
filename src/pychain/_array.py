from collections.abc import Callable
from typing import TYPE_CHECKING, Concatenate, Self

import numbagg as nbg
import numpy as np
import rustats as rs
from numpy.typing import NDArray

from ._core import CommonBase, iter_on

if TYPE_CHECKING:
    from ._iter import Iter

type Numeric = np.floating | np.integer | np.unsignedinteger

type NumpyType = Numeric | np.bool_
type IntoArr[T: NumpyType] = NDArray[T] | float | int
type ArrFunc[T: NumpyType] = Callable[..., NDArray[T]]


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

    def add(self, other: IntoArr[T]) -> Self:
        return self._new(np.add(self._data, other))

    def sub(self, other: IntoArr[T]) -> Self:
        return self._new(np.subtract(self._data, other))

    def sub_r(self, other: IntoArr[T]) -> Self:
        return self._new(np.subtract(other, self._data))

    def mul(self, other: IntoArr[T]) -> Self:
        return self._new(np.multiply(self._data, other))

    def truediv(self, other: IntoArr[T]) -> Self:
        return self._new(np.divide(self._data, other))

    def truediv_r(self, other: IntoArr[T]) -> Self:
        return self._new(np.divide(other, self._data))

    def floor_div(self, other: IntoArr[T]) -> Self:
        return self._new(np.floor_divide(self._data, other))

    def floor_div_r(self, other: IntoArr[T]) -> Self:
        return self._new(np.floor_divide(other, self._data))

    def sign(self) -> Self:
        return self._new(np.sign(self._data))

    def abs(self) -> Self:
        return self._new(np.abs(self._data))

    def sqrt(self) -> Self:
        return self._new(np.sqrt(self._data))

    def pow(self, exponent: int) -> Self:
        return self._new(np.power(self._data, exponent))

    def neg(self) -> Self:
        return self._new(np.negative(self._data))

    def rolling_mean[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_mean(self._data, window_size, min_samples))

    def rolling_median[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_median(self._data, window_size, min_samples))

    def rolling_max[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_max(self._data, window_size, min_samples))

    def rolling_min[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_min(self._data, window_size, min_samples))

    def rolling_sum[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_sum(self._data, window_size, min_samples))

    def rolling_std[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_std(self._data, window_size, min_samples))

    def rolling_var[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_var(self._data, window_size, min_samples))

    def rolling_skew[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_skewness(self._data, window_size, min_samples))

    def rolling_kurtosis[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_kurtosis(self._data, window_size, min_samples))

    def rolling_rank[U: np.floating](
        self: "Array[U]",
        window_size: int,
        min_samples: int,
    ) -> "Array[U]":
        return self._new(rs.move_rank(self._data, window_size, min_samples))

    def forward_fill[U: np.floating](
        self: "Array[U]", limit: int, axis: int
    ) -> "Array[U]":
        return self._new(nbg.ffill(self._data, limit=limit, axis=axis))

    def backward_fill[U: np.floating](
        self: "Array[U]", limit: int, axis: int
    ) -> "Array[U]":
        return self._new(nbg.bfill(self._data, limit=limit, axis=axis))

    def into_iter(self) -> "Iter[T]":
        return iter_on(self._data)
