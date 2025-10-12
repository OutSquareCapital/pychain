from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Concatenate, Self

from .._expressions import Expr
from ._core import CoreDict


class Record(CoreDict[str, Any]):
    def pipe_into[**P](
        self,
        func: Callable[Concatenate[dict[str, Any], P], dict[str, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Record:
        """
        Apply a function to the underlying dict and return a new Record.

        >>> from pychain import Record
        >>>
        >>> def mul_by_ten(d: dict[int, int]) -> dict[int, int]:
        ...     return {k: v * 10 for k, v in d.items()}
        >>>
        >>> Record({1: 20, 2: 30}).pipe_into(mul_by_ten).unwrap()
        {1: 200, 2: 300}
        """
        return Record(func(self._data, *args, **kwargs))

    def _from_context(
        self, data: dict[str, Any], plan: Iterable[Expr], is_selection: bool
    ) -> Self:
        if is_selection:
            result_dict: dict[str, Any] = {}
        else:
            result_dict = self._data.copy()

        for expr in plan:
            expr.__compute__(data, result_dict)

        return self._new(result_dict)

    def select(self, *exprs: Expr) -> Self:
        """
        Select only the specified fields, creating a new dictionary with just those fields.
        """
        return self._from_context(self._data, exprs, True)

    def with_fields(self, *exprs: Expr) -> Self:
        """
        Adds or replaces fields in the existing dictionary.
        """
        return self._from_context(self._data, exprs, False)
