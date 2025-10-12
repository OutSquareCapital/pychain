from __future__ import annotations

import operator
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Concatenate, Self, TypeGuard

from .._core import Pipeable

if TYPE_CHECKING:
    pass

type ExprOp = Callable[[dict[str, Any]], Any]


def _identity(x: Any) -> Any:
    return x


@dataclass(slots=True)
class Expr(Pipeable):
    _operation: ExprOp
    _output_name: str
    _is_pychain_expr = True

    def __compute__(self, input: dict[str, Any], output: dict[str, Any]):
        value = self._operation(input)
        output[self._output_name] = value

    def _new[**P](
        self,
        operation: Callable[Concatenate[dict[str, Any], P], Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        return self.__class__(
            lambda data: operation(data, *args, **kwargs), self._output_name
        )

    @staticmethod
    def is_expr(obj: Any) -> TypeGuard[Expr]:
        return hasattr(obj, "_is_pychain_expr")

    def alias(self, name: str) -> Expr:
        """Définit le nom de la clé dans le dictionnaire de sortie."""
        self._output_name = name
        return self

    # --- Accesseurs ---
    def field(self, name: str | int) -> Self:
        """Accède à une clé ou un index imbriqué."""

        def operation(data: dict[str, Any]) -> Any:
            try:
                return self._operation(data)[name]
            except (KeyError, IndexError, TypeError) as e:
                raise e.__class__(f"Clé ou index '{name}' invalide.") from e

        return self._new(operation)

    def _arithmetic_op(self, op_func: Callable[[Any, Any], Any], other: Any) -> Self:
        other_op = other._operation if Expr.is_expr(other) else _identity
        return self._new(lambda data: op_func(self._operation(data), other_op(data)))

    # --- Opérations Arithmétiques ---
    def add(self, other: Any) -> Self:
        return self._new(operator.add, other)

    def sub(self, other: Any) -> Self:
        return self._new(operator.sub, other)

    def mul(self, other: Any) -> Self:
        return self._new(operator.mul, other)

    def truediv(self, other: Any) -> Self:
        return self._new(operator.truediv, other)

    def floor_div(self, other: Any) -> Self:
        return self._new(operator.floordiv, other)

    # --- Opérations de Comparaison ---
    def eq(self, other: Any) -> Self:
        return self._new(operator.eq, other)

    def neq(self, other: Any) -> Self:
        return self._new(operator.ne, other)

    def gt(self, other: Any) -> Self:
        return self._arithmetic_op(operator.gt, other)

    def gte(self, other: Any) -> Self:
        return self._arithmetic_op(operator.ge, other)

    def lt(self, other: Any) -> Self:
        return self._arithmetic_op(operator.lt, other)

    def lte(self, other: Any) -> Self:
        return self._arithmetic_op(operator.le, other)

    # --- Opérations Logiques ---
    def and_(self, other: Expr) -> Self:
        return self._new(lambda data: self._operation(data) and other._operation(data))

    def or_(self, other: Expr) -> Self:
        return self._new(lambda data: self._operation(data) or other._operation(data))

    def not_(self) -> Self:
        return self._new(lambda data: not self._operation(data))

    def apply(self, func: Callable[[Any], Any]) -> Self:
        return self._new(lambda data: func(self._operation(data)))


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr(lambda data: data[name], name)

    def __get_attr__(self, name: str) -> Expr:
        return self(name)


key = KeySelector()
