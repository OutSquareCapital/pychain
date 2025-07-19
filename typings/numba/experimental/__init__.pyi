from collections.abc import Iterable, Callable
from typing import Any, overload

@overload
def jitclass[T: type](
    cls_or_spec: T, spec: Iterable[tuple[str, Any]] | dict[str, Any]
) -> T:
    """Function to JIT-compile a class with a specified type signature."""
    ...

@overload
def jitclass[T: type](
    cls_or_spec: Iterable[tuple[str, Any]] | dict[str, Any] | None = None,
    spec: Iterable[tuple[str, Any]] | dict[str, Any] | None = None,
) -> Callable[[T], T]:
    """Decorator to JIT-compile a class with a specified type signature."""
    ...
