from ._core import BaseExpr
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING
import cytoolz.itertoolz as itz
from functools import partial
from ._protocols import ProcessFunc

if TYPE_CHECKING:
    from ._iter import Iter


class Expr[P, R](BaseExpr[P, R]):
    __slots__ = "_pipeline"

    def _do[T](self, f: Callable[[R], T]) -> "Expr[P, T]":
        return Expr(self._pipeline + [f])

    def do(self, f: ProcessFunc[R]) -> "Expr[P, R]":
        return self._do(f)

    def into[T](self, obj: Callable[[R], T]) -> "Expr[P, T]":
        return self._do(obj)

    def into_expr[T](self, obj: T) -> "Expr[P, T]":
        return self._do(obj)  # type: ignore

    def into_iter[T](self, f: Callable[[R], Iterable[T]]) -> "Iter[P, T]":
        return Iter(self._pipeline + [f])

    def into_iter_func[T](self, f: Callable[[R], T]) -> "Iter[P, T]":
        return Iter(self._do(partial(itz.iterate, f))._pipeline)
