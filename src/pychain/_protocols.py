from collections.abc import Callable
from typing import Any
from dataclasses import dataclass
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


@dataclass(slots=True, frozen=True, repr=False)
class Func[P, R]:
    """
    A frozen dataclass that represents a compiled function with source code.

    This allows you to take advantage of this class for development purposes, and then extract the function for production deployments.

    Provides:
        - A repr for easy debugging
        - A convenient way to type hint the function(without having to import from collections.abc.... and the long typing syntax)
        - A `numbify` method to compile the function with numba for potential performance improvements.
        - An `extract` method to return the wrapped func. Use it for production code.
    """

    _compiled_func: Callable[[P], R]
    _source_code: str

    def __call__(self, arg: P) -> R:
        return self._compiled_func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self._source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"

    def numbify(self) -> "Func[P, R]":
        from numba import jit

        try:
            compiled_func: Callable[[P], R] = jit(self._compiled_func)
        except Exception as e:
            print(f"Failed to compile function: {e}")
            return self
        return Func(compiled_func, self._source_code)

    def extract(self) -> Callable[[P], R]:
        """
        Returns the wrapped function.
        """
        return self._compiled_func
