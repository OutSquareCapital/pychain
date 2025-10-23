from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Self, TypeGuard

import cytoolz as cz

from .._core import Pipeable


@dataclass(slots=True)
class Expr(Pipeable):
    """
    Represents an expression in the pipeline.

    An Expr encapsulates a sequence of operations to be applied to keys on a python dict.

    Each Expr instance maintains:
    - A list of tokens representing the keys to access in the dict (the first being the input given to the `key` function),
    - A tuple of operations to apply to the accessed data
    - An alias for the expression (default to the last token).
    """

    __tokens__: list[str]
    __ops__: tuple[Callable[[object], object], ...]
    _alias: str

    def __repr__(self) -> str:
        parts: list[str] = []
        s_parts: list[str] = []
        for t in self.__tokens__:
            parts.append(f"field({t!r})")
            if s_parts:
                s_parts.append(".")
            s_parts.append(str(t))
        symbolic = ".".join(parts) if parts else "<root>"
        lowered = "".join(s_parts) or "<root>"
        base = f"Expr({symbolic} -> {lowered})"
        return f"{base}.alias({self._alias!r})"

    def _to_expr(self, op: Callable[[Any], Any]) -> Self:
        return self.__class__(
            self.__tokens__,
            self.__ops__ + (op,),
            self._alias,
        )

    def key(self, name: str) -> Self:
        """
        Add a key to the expression.

        Allow to access nested keys in a dict.

        Args:
            name: The key to access.
        Example:
        ```python
        >>> import pyochain as pc
        >>> expr = pc.key("a").key("b").key("c")
        >>> expr.__tokens__
        ['a', 'b', 'c']
        >>> data = {"a": {"b": {"c": 42}}}
        >>> pc.Dict(data).select(expr).unwrap()
        {'c': 42}

        ```
        """
        return self.__class__(
            self.__tokens__ + [name],
            self.__ops__,
            name,
        )

    def alias(self, name: str) -> Self:
        return self.__class__(self.__tokens__, self.__ops__, name)

    @property
    def name(self) -> str:
        return self._alias

    def apply(self, fn: Callable[[Any], Any]) -> Self:
        """
        Applies the given function fn to the data within the current Expr instance
        """

        def _apply(data: Any) -> Any:
            return fn(data)

        return self._to_expr(_apply)


def key(name: str) -> Expr:
    """Create an Expr that accesses the given key."""
    return Expr([name], (), name)


def _expr_identity(obj: Any) -> TypeGuard[Expr]:
    return hasattr(obj, "__tokens__")


type IntoExpr = Expr | str


def compute_exprs(
    exprs: Iterable[IntoExpr], data_in: dict[str, Any], data_out: dict[str, Any]
) -> dict[str, Any]:
    for e in exprs:
        if not _expr_identity(e):
            e = key(e)  # type: ignore
        current: object = cz.dicttoolz.get_in(e.__tokens__, data_in)
        for op in e.__ops__:
            current = op(current)
        data_out[e.name] = current
    return data_out
