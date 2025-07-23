from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Placeholder[T]:
    _is_pychain_arg: bool = True

    def __repr__(self) -> str:
        return "PIPE_ARG"


@dataclass(frozen=True, slots=True)
class PlaceholderConstructor:
    def __call__[T](self, dtype: type[T] | T) -> T:
        return Placeholder()  # type: ignore


def is_placeholder(obj: Any) -> bool:
    return getattr(obj, "_is_pychain_arg", False) is True


pipe_arg = PlaceholderConstructor()


@dataclass(frozen=True, slots=True)
class Operation[R, **P]:
    func: Callable[P, R]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
