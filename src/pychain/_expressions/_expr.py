from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self, TypeGuard, final

import cytoolz as cz

from .._executors import Executor

type IntoExpr = str | Expr


def is_expr(obj: Any) -> TypeGuard[Expr]:
    return getattr(obj, "_is_pychain_expr", False)


def parse_expr(expr: IntoExpr) -> Expr:
    match expr:
        case Expr():
            return expr
        case str():
            return key(expr)
        case _:
            raise TypeError(f"Expression must be of type str or Expr, not {type(expr)}")


@final
@dataclass(slots=True)
class Expr(Executor[Any]):
    _input_name: str
    _output_name: str
    _is_pychain_expr = True
    _operations: list[Callable[[Any], Any]]

    @property
    def _func(self) -> Callable[[Any], Any]:
        return cz.functoolz.compose_left(*self._operations)

    def __compute__(self, input: dict[str, Any], output: dict[str, Any]) -> None:
        output[self._output_name] = self._func(input[self._input_name])

    def _new(self, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Self:
        return self.__class__(
            self._input_name, self._output_name, self._operations + [func]
        )

    def into(self, func: Callable[[Any], Any]) -> Self:
        return self._new(func)

    def alias(self, name: str) -> Expr:
        self._output_name = name
        return self

    def field(self, name: str | int) -> Self:
        def operation(data: dict[Any, Any]) -> Any:
            try:
                return self._func(data).get(name)
            except (KeyError, IndexError, TypeError) as e:
                raise e.__class__(f"Clé ou index '{name}' invalide.") from e

        return self._new(operation)

    def apply(self, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Self:
        return self._new(func)

    def add(self, value: Any) -> Self:
        return self._new(lambda x: x + value)

    def mul(self, value: Any) -> Self:
        return self._new(lambda x: x * value)

    def sub(self, value: Any) -> Self:
        return self._new(lambda x: x - value)

    def rsub(self, value: Any) -> Self:
        return self._new(lambda x: value - x)

    def truediv(self, value: Any) -> Self:
        return self._new(lambda x: x / value)

    def rtruediv(self, value: Any) -> Self:
        return self._new(lambda x: value / x)

    def floordiv(self, value: Any) -> Self:
        return self._new(lambda x: x // value)

    def rfloordiv(self, value: Any) -> Self:
        return self._new(lambda x: value // x)

    def mod(self, value: Any) -> Self:
        return self._new(lambda x: x % value)

    def pow(self, value: Any) -> Self:
        return self._new(lambda x: x**value)

    def neg(self) -> Self:
        return self._new(lambda x: -x)

    def pos(self) -> Self:
        return self._new(lambda x: +x)

    def abs(self) -> Self:
        return self._new(abs)

    def not_(self) -> Self:
        return self._new(lambda x: not x)

    def and_(self, value: Any) -> Self:
        return self._new(lambda x: x and value)

    def or_(self, value: Any) -> Self:
        return self._new(lambda x: x or value)

    def eq(self, value: Any) -> Self:
        return self._new(lambda x: x == value)

    def ne(self, value: Any) -> Self:
        return self._new(lambda x: x != value)

    def lt(self, value: Any) -> Self:
        return self._new(lambda x: x < value)

    def le(self, value: Any) -> Self:
        return self._new(lambda x: x <= value)

    def gt(self, value: Any) -> Self:
        return self._new(lambda x: x > value)

    def ge(self, value: Any) -> Self:
        return self._new(lambda x: x >= value)


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr(name, name, [cz.functoolz.identity])

    def __get_attr__(self, name: str) -> Expr:
        return self(name)


key = KeySelector()
