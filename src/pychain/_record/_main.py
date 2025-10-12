from __future__ import annotations

from collections.abc import Callable
from typing import Any, Concatenate, Self

from .._core import CommonBase
from ._expr import Expr


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr(lambda data: data[name]).alias(name)

    def __get_attr__(self, name: str) -> Expr:
        return self(name).alias(name)


key = KeySelector()


class Record(CommonBase[dict[str, Any]]):
    _is_selection: bool
    _plan: list[Expr]

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

        return self._new(result_dict)

    def pipe_into[**P](
        self,
        func: Callable[Concatenate[dict[str, Any], P], dict[str, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Record:
        """
        Apply a function to the underlying dict and return a new Record.

        >>> from pychain import Dict
        >>>
        >>> def mul_by_ten(d: dict[int, int]) -> dict[int, int]:
        ...     return {k: v * 10 for k, v in d.items()}
        >>>
        >>> data = {"a": 20, "b": 30}
        >>> Record(data).pipe_into(mul_by_ten).select(key("b")).collect().unwrap()
        {'b': 300}
        """
        return Record(func(self._data, *args, **kwargs))
