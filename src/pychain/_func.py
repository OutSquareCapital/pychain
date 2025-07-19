import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


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

    def __call__(self, arg: Any) -> Any:
        return self._compiled_func(arg)

    def __repr__(self) -> str:
        signature: str = self._source_code.splitlines()[0]
        indented_code: str = textwrap.indent(self._source_code, "    ")
        return f"pychain.Func({signature})\n-- Source --\n{indented_code}"

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
