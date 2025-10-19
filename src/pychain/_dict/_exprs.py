from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Self, TypeGuard

import cytoolz as cz

from .._core import Pipeable


@dataclass(slots=True)
class Expr(Pipeable):
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
        return self._to_expr(lambda data: fn(data))


def key(name: str) -> Expr:
    return Expr([name], (), name)


def _expr_identity(obj: Any) -> TypeGuard[Expr]:
    return hasattr(obj, "__tokens__")


type IntoExpr = Expr | str


def compute_exprs(
    exprs: Iterable[IntoExpr], data_in: dict[str, Any], data_out: dict[str, Any]
) -> dict[str, Any]:
    for e in exprs:
        if not _expr_identity(e):
            e = Expr([], (), e)  # type: ignore[misc]
        current: object = cz.dicttoolz.get_in(e.__tokens__, data_in)
        for op in e.__ops__:
            current = op(current)
        data_out[e.name] = current
    return data_out
