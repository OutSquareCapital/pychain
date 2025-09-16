from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, Concatenate, Protocol

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._iter import Iter


class NPTypeLike[T](Protocol): ...


class NPArrayLike[S, D: NPTypeLike[Any]](Protocol):
    """Array protocol to support numpy arrays and similar objects, without needing numpy as an explicit dependency."""

    def __iter__(self) -> Iterator[D]: ...
    def __array__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __array_finalize__(self, *args: Any, **kwargs: Any) -> None: ...
    def __array_wrap__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __getitem__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __setitem__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def shape(self) -> S: ...
    @property
    def dtype(self) -> Any: ...
    @property
    def ndim(self) -> int: ...
    @property
    def size(self) -> int: ...


type NDArray[T: NPTypeLike[Any]] = NPArrayLike[tuple[int, ...], T]


class Array[T: NDArray[Any]](CommonBase[T]):
    """
    Wrapper for numpy arrays and similar objects.
    This is a simple class but that allows to use the same API as the other wrappers.
    It is mainly useful to chain operations on numpy arrays.

        >>> import numpy as np
        >>> import pychain as pc
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> pc.Array(data).pipe_chain(lambda x: x + 2, lambda x: x * 3).pipe_unwrap(
        ...     lambda x: x.clip(10, 20)
        ... )
        array([10, 12, 15, 18, 20])
    """

    __slots__ = "_data"
    _data: T

    def pipe_unwrap[**P, U: NDArray[Any]](
        self,
        func: Callable[
            Concatenate[T, P],
            U,
        ],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Array[U]":
        """Apply a function to the wrapped data and return a new Array wrapping the result."""
        return Array(func(self._data, *args, **kwargs))

    def to_iter(self) -> "Iter[T]":
        """
        Convert the wrapped array to an Iter wrapper.
        """
        return iter_factory(self._data)
