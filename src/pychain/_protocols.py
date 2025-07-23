from collections.abc import Callable, Iterable
from typing import Any
from dataclasses import dataclass


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


type Scope = dict[str, Any]
type CheckFunc[T] = Callable[[T], bool]
type ProcessFunc[T] = Callable[[T], T]
type TransformFunc[T, T1] = Callable[[T], T1]
type AggFunc[V, V1] = Callable[[Iterable[V]], V1]
type ThreadFunc[T] = Callable[..., T] | tuple[Callable[..., T], Any]
type CompileResult[T] = tuple[Callable[[T], Any], str]
INLINEABLE_BUILTINS: set[type | Callable[..., Any]] = {
    int,
    str,
    float,
    list,
    dict,
    tuple,
    set,
    len,
    round,
    repr,
    sum,
    max,
    min,
    abs,
    all,
    any,
    sorted,
    reversed,
    iter,
    next,
    zip,
    enumerate,
    range,
    map,
    filter,
}
