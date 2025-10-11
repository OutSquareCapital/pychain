from __future__ import annotations

from collections.abc import Callable
from typing import Any, Concatenate, Self

from ._expr import Expr


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr(lambda data: data[name]).alias(name)

    def __get_attr__(self, name: str) -> Expr:
        return self(name).alias(name)


key = KeySelector()


class Record:
    _is_selection: bool
    _plan: list[Expr]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data: dict[str, Any] = data

    def __repr__(self) -> str:
        data_formatted: str = "\n".join(
            f"  {key!r}, {type(value).__name__}: {value!r},"
            for key, value in self._data.items()
        )
        return f"Record(\n{data_formatted}\n)"

    @classmethod
    def _from_context(
        cls, data: dict[str, Any], plan: list[Expr], is_selection: bool
    ) -> Self:
        instance: Self = cls(data)
        instance._plan = plan
        instance._is_selection = is_selection
        return instance

    def select(self, *exprs: Expr) -> Self:
        """
        Select only the specified fields, creating a new dictionary with just those fields.
        """
        return self._from_context(self._data, list(exprs), True)

    def with_fields(self, *exprs: Expr) -> Self:
        """
        Adds or replaces fields in the existing dictionary.
        """
        return self._from_context(self._data, list(exprs), False)

    def collect(self) -> Self:
        """
        Execute the planned transformations and return the resulting dictionary.
        """
        if not self._plan:
            return self

        if self._is_selection:
            result_dict: dict[str, Any] = {}
        else:
            result_dict = self._data.copy()

        for expr in self._plan:
            value = expr.__evaluate__(self._data)
            result_dict[expr.__expr_name__()] = value

        return self.__class__(result_dict)

    def unwrap(self) -> dict[str, Any]:
        """
        Return the underlying data.

        This is a terminal operation.
        """
        return self._data

    def pipe[**P, R](
        self,
        func: Callable[Concatenate[Self, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """Pipe the instance in the function and return the result."""
        return func(self, *args, **kwargs)
