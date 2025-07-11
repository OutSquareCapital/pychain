from collections.abc import Callable, Container
from dataclasses import dataclass, field
from typing import Any, Self

from .. import fn


@dataclass(slots=True, frozen=True)
class ChainableOp:
    _pipeline: Callable[[Any], Any] = field(default=lambda x: x)

    def __call__(self, value: Any) -> Any:
        return self._pipeline(value)

    def _chain(self, new_op: Callable[[Any], Any]) -> Self:
        def composed(x: Any) -> Any:
            return new_op(self._pipeline(x))

        return self.__class__(_pipeline=composed)

    def attr(self, *names: str) -> Self:
        return self._chain(fn.attr(*names))

    def item(self, *keys: Any) -> Self:
        return self._chain(fn.item(*keys))

    def method(self, name: str, *args: Any, **kwargs: Any) -> Self:
        return self._chain(fn.method(name, *args, **kwargs))

    def add(self, value: Any) -> Self:
        return self._chain(fn.add(value))

    def sub(self, value: Any) -> Self:
        return self._chain(fn.sub(value))

    def mul(self, value: Any) -> Self:
        return self._chain(fn.mul(value))

    def truediv(self, value: Any) -> Self:
        return self._chain(fn.truediv(value))

    def floordiv(self, value: Any) -> Self:
        return self._chain(fn.floordiv(value))

    def sub_r(self, value: Any) -> Self:
        return self._chain(fn.sub_r(value))

    def truediv_r(self, value: Any) -> Self:
        return self._chain(fn.truediv_r(value))

    def floordiv_r(self, value: Any) -> Self:
        return self._chain(fn.floordiv_r(value))

    def mod(self, value: Any) -> Self:
        return self._chain(fn.mod(value))

    def pow(self, value: Any) -> Self:
        return self._chain(fn.pow(value))

    def neg(self) -> Self:
        return self._chain(fn.neg)

    def is_true(self) -> Self:
        return self._chain(fn.is_true)

    def is_none(self) -> Self:
        return self._chain(fn.is_none())

    def is_not_none(self) -> Self:
        return self._chain(fn.is_not_none())

    def is_in(self, values: Container[Any]) -> Self:
        return self._chain(fn.is_in(values))

    def is_not_in(self, values: Container[Any]) -> Self:
        return self._chain(fn.is_not_in(values))

    def is_distinct(self) -> Self:
        return self._chain(fn.is_distinct)

    def is_iterable(self) -> Self:
        return self._chain(fn.is_iterable)

    def is_all(self) -> Self:
        return self._chain(fn.is_all)

    def is_any(self) -> Self:
        return self._chain(fn.is_any)

    def eq(self, value: Any) -> Self:
        return self._chain(fn.eq(value))

    def ne(self, value: Any) -> Self:
        return self._chain(fn.ne(value))

    def gt(self, value: Any) -> Self:
        return self._chain(fn.gt(value))

    def ge(self, value: Any) -> Self:
        return self._chain(fn.ge(value))

    def lt(self, value: Any) -> Self:
        return self._chain(fn.lt(value))

    def le(self, value: Any) -> Self:
        return self._chain(fn.le(value))
