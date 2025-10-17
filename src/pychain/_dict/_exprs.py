from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

import cytoolz as cz

from .._core import Pipeable


@dataclass(slots=True)
class Expr(Pipeable):
    __tokens__: list[str]
    __ops__: tuple[Callable[[object], object], ...]
    _alias: str

    def expr_repr(self) -> str:
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

    def __getattr__(self, name: str) -> Self:
        return self.key(name)

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

    def pluck(self, *names: str) -> Self:
        """
        Returns a new Expr with values extracted from each item in the data using the specified names as paths.

        Uses cz.dicttoolz.get_in to retrieve nested values
        """
        return self._to_expr(
            lambda data: [cz.dicttoolz.get_in(names, data) for data in data]
        )

    def keys(self) -> Self:
        """
        Returns a new Expr representing the dictionary keys of the current expression
        """
        return self._to_expr(lambda v: v.keys())

    def values(self) -> Self:
        """
        Returns a new Expr representing the dictionary values of the current expression
        """
        return self._to_expr(lambda v: v.values())

    def apply(self, fn: Callable[[Any], Any]) -> Self:
        """
        Applies the given function fn to the data within the current Expr instance
        """
        return self._to_expr(lambda data: fn(data))


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr([name], (), name)

    def __getattr__(self, name: str) -> Expr:
        return self(name)


key = KeySelector()
