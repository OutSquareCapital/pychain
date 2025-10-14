from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Concatenate

from .._core import EagerWrapper

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter


class Wrapper[T](EagerWrapper[T]):
    """
    A generic Wrapper for any type.
    The pipe into method is implemented to return a Wrapper of the result type.

    This class is intended for use with other types/implementations that do not support the fluent/functional style.
    This allow the use of a consistent code style across the code base.
    """

    def apply[**P, R](
        self,
        func: Callable[Concatenate[T, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Wrapper[R]:
        """
        Pipe the underlying data into a function, then wrap the result in a new `Wrapper` instance.

        Note that if the generic type `R` is itself a generic type, the resulting `Wrapper` will not retain that information in some cases.

        This is a limitation of Python's type system for generics.

        This is also why pipe into is an abstract method in `CommonBase`, altough `Dict` and `Iter` have the exact same implementation.
        """
        return Wrapper(self.into(func, *args, **kwargs))

    def to_iter[U: Iterable[Any]](self: Wrapper[U]) -> Iter[U]:
        """
        Convert the wrapped data to an Iter wrapper.
        """
        from ._iter import Iter

        return self.into(Iter)

    def to_dict[KU, VU](self: Wrapper[dict[KU, VU]]) -> Dict[KU, VU]:
        """
        Convert the wrapped dict to a Dict wrapper.

            >>> import pychain as pc
            >>>
            >>> data = {1: "a", 2: "b"}
            >>>
            >>> pc.Wrapper(data).to_dict().unwrap()
            {1: 'a', 2: 'b'}
        """
        from ._dict import Dict

        return self.into(Dict)
