from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
import textwrap


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


class Func[P, R]:
    def __init__(
        self, compiled_func: Callable[[P], R], source_code: str, scope: dict[str, Any]
    ):
        self.compiled_func = compiled_func
        self.source_code = source_code
        self.scope = scope

    def __call__(self, arg: P) -> R:
        return self.compiled_func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self.source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"

    def extract(self) -> Callable[[P], R]:
        return self.compiled_func
