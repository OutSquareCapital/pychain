from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

import cytoolz as cz

from .._core import Pipeable

type ExprOp = Callable[[dict[Any, Any]], Any]


@dataclass(slots=True)
class Expr(Pipeable):
    _input_name: str
    _output_name: str
    _is_pychain_expr = True
    _operations: list[ExprOp]

    @property
    def func(self) -> ExprOp:
        return cz.functoolz.compose_left(*self._operations)

    def __compute__(self, input: dict[str, Any], output: dict[str, Any]):
        output[self._output_name] = self.func(input[self._input_name])

    def _new(self, operation: ExprOp) -> Self:
        return self.__class__(
            self._input_name, self._output_name, self._operations + [operation]
        )

    def alias(self, name: str) -> Expr:
        self._output_name = name
        return self

    def field(self, name: str | int) -> Self:
        def operation(data: dict[Any, Any]) -> Any:
            try:
                return self.func(data)[name]
            except (KeyError, IndexError, TypeError) as e:
                raise e.__class__(f"Clé ou index '{name}' invalide.") from e

        return self._new(operation)

    def apply(self, func: Callable[[Any], Any]) -> Self:
        return self._new(func)


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr(name, name, [lambda data: data])

    def __get_attr__(self, name: str) -> Expr:
        return self(name)


key = KeySelector()
