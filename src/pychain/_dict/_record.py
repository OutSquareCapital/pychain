from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Concatenate, Self, final

from .._expressions import IntoExpr, parse_expr
from ._core import CoreDict


@final
class Record(CoreDict[str, Any]):
    def apply[**P](
        self,
        func: Callable[Concatenate[dict[str, Any], P], dict[str, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        """
        Apply a function to the underlying dict and return a new Record.

        >>> from pychain import Record
        >>>
        >>> def mul_by_ten(d: dict[int, int]) -> dict[int, int]:
        ...     return {k: v * 10 for k, v in d.items()}
        >>>
        >>> Record({1: 20, 2: 30}).apply(mul_by_ten).unwrap()
        {1: 200, 2: 300}
        """
        return self.__class__(self.into(func, *args, **kwargs))

    def _from_context(self, plan: Iterable[IntoExpr], is_selection: bool) -> Self:
        def _(data: dict[str, Any]) -> dict[str, Any]:
            if is_selection:
                result_dict: dict[str, Any] = {}
            else:
                result_dict = data.copy()

            for expr in plan:
                parse_expr(expr).__compute__(data, result_dict)

            return result_dict

        return self._new(_)

    def select(self, *exprs: IntoExpr) -> Self:
        """
        Select only the specified fields, creating a new dictionary with just those fields.
        """
        return self._from_context(exprs, True)

    def with_fields(self, *exprs: IntoExpr) -> Self:
        """
        Adds or replaces fields in the existing dictionary.
        """
        return self._from_context(exprs, False)
