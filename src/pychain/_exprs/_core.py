from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

@dataclass(slots=True, frozen=True)
class BaseChainableOp:
    _pipeline: Callable[[Any], Any] = field(default=lambda x: x)

    def __call__(self, value: Any) -> Any:
        return self._pipeline(value)

    def _chain(self, new_op: Callable[[Any], Any]) -> Self:
        def composed(x: Any) -> Any:
            return new_op(self._pipeline(x))

        return self.__class__(_pipeline=composed)

    def __add__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) + other(value)

        return self.__class__(_pipeline=combined_logic)

    def __radd__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other + self(value)

        return self.__class__(_pipeline=combined_logic)

    def __sub__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) - other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rsub__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other - self(value)

        return self.__class__(_pipeline=combined_logic)

    def __mul__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) * other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rmul__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other * self(value)

        return self.__class__(_pipeline=combined_logic)

    def __truediv__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) / other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rtruediv__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other / self(value)

        return self.__class__(_pipeline=combined_logic)

    def __floordiv__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) // other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rfloordiv__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other // self(value)

        return self.__class__(_pipeline=combined_logic)

    def __mod__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) % other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rmod__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other % self(value)

        return self.__class__(_pipeline=combined_logic)

    def __pow__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) ** other(value)

        return self.__class__(_pipeline=combined_logic)

    def __rpow__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return other ** self(value)

        return self.__class__(_pipeline=combined_logic)

    def __neg__(self) -> Self:
        def neg_logic(value: Any) -> Any:
            return -self(value)

        return self.__class__(_pipeline=neg_logic)

    def __pos__(self) -> Self:
        def pos_logic(value: Any) -> Any:
            return +self(value)

        return self.__class__(_pipeline=pos_logic)

    def __invert__(self) -> Self:
        def invert_logic(value: Any) -> Any:
            return ~self(value)

        return self.__class__(_pipeline=invert_logic)

    def __and__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) and other(value)

        return self.__class__(_pipeline=combined_logic)

    def __or__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) or other(value)

        return self.__class__(_pipeline=combined_logic)

    def __xor__(self, other: Self) -> Self:
        def combined_logic(value: Any) -> bool:
            return self(value) ^ other(value)

        return self.__class__(_pipeline=combined_logic)
