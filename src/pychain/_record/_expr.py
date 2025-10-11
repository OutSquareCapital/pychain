from __future__ import annotations

import operator
from collections.abc import Callable
from typing import Any, Concatenate, Self, TypeGuard

from .._dict import Dict
from .._iter import Iter

type ExprOp = Callable[[dict[str, Any]], Any]


def _identity(x: Any) -> Any:
    return x


class Expr:
    _operation: ExprOp
    _is_pychain_expr = True
    _output_name: str = "<unnamed>"

    def __init__(self, operation: ExprOp) -> None:
        self._operation = operation

    def __expr_name__(self) -> str:
        return self._output_name

    @staticmethod
    def is_expr(obj: Any) -> TypeGuard[Expr]:
        return hasattr(obj, "_is_pychain_expr")

    def __evaluate__(self, data: dict[str, Any]) -> Any:
        """Exécute l'opération sur les données."""
        return self._operation(data)

    def alias(self, name: str) -> Expr:
        """Définit le nom de la clé dans le dictionnaire de sortie."""
        self._output_name = name
        return self

    # --- Accesseurs ---
    def field(self, name: str | int) -> Self:
        """Accède à une clé ou un index imbriqué."""

        def operation(data: dict[str, Any]) -> Any:
            try:
                return self.__evaluate__(data)[name]
            except (KeyError, IndexError, TypeError) as e:
                # Gérer les accès invalides de manière plus robuste si nécessaire
                raise e.__class__(f"Clé ou index '{name}' invalide.") from e

        return self.__class__(operation)

    def _arithmetic_op(self, op_func: Callable[[Any, Any], Any], other: Any) -> Self:
        other_op = other._operation if Expr.is_expr(other) else _identity
        return self.__class__(
            lambda data: op_func(self.__evaluate__(data), other_op(data))
        )

    # --- Opérations Arithmétiques ---
    def add(self, other: Any) -> Self:
        return self._arithmetic_op(operator.add, other)

    def sub(self, other: Any) -> Self:
        return self._arithmetic_op(operator.sub, other)

    def mul(self, other: Any) -> Self:
        return self._arithmetic_op(operator.mul, other)

    def truediv(self, other: Any) -> Self:
        return self._arithmetic_op(operator.truediv, other)

    def floor_div(self, other: Any) -> Self:
        return self._arithmetic_op(operator.floordiv, other)

    # --- Opérations de Comparaison ---
    def eq(self, other: Any) -> Self:
        return self._arithmetic_op(operator.eq, other)

    def neq(self, other: Any) -> Self:
        return self._arithmetic_op(operator.ne, other)

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
        return self.__class__(
            lambda data: self.__evaluate__(data) and other.__evaluate__(data)
        )

    def or_(self, other: Expr) -> Self:
        return self.__class__(
            lambda data: self.__evaluate__(data) or other.__evaluate__(data)
        )

    def not_(self) -> Self:
        return self.__class__(lambda data: not self.__evaluate__(data))

    def cast(self, to_type: type) -> Self:
        """Casts the result of the expression to a specified type."""
        return self.__class__(lambda data: to_type(self.__evaluate__(data)))

    # --- Opérations sur les listes/iterables ---

    # --- Transformations ---
    def apply(self, func: Callable[[Any], Any]) -> Self:
        """Applique une fonction personnalisée au résultat de l'expression."""
        return self.__class__(lambda data: func(self.__evaluate__(data)))

    def itr_apply(self, func: Callable[[Iter[Any]], Any]) -> Self:
        """Applique une fonction personnalisée au résultat de l'expression, en supposant que c'est un itérable."""
        return self.__class__(lambda data: func(Iter(self.__evaluate__(data))))

    def struct_apply(self, func: Callable[[Dict[str, Any]], Any]) -> Self:
        """Applique une fonction personnalisée au résultat de l'expression, en supposant que c'est un dict."""
        return self.__class__(lambda data: func(Dict(self.__evaluate__(data))))

    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)
