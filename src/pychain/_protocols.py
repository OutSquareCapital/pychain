import builtins
import textwrap
from collections.abc import Callable, Iterable
from enum import StrEnum, auto
from typing import Any, NamedTuple


class Placeholder[T](NamedTuple):
    is_pychain_arg: bool = True


class Operation[R, **P](NamedTuple):
    func: Callable[P, R]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


def get_placeholder[T](dtype: type[T] | T) -> T:
    return Placeholder()  # type: ignore


def is_placeholder(obj: Any) -> bool:
    return getattr(obj, "is_pychain_arg", False) is True


class Func[P, R]:
    def __init__(
        self, compiled_func: Callable[[P], R], source_code: str, scope: dict[str, Any]
    ):
        self.func = compiled_func
        self.source_code = source_code
        self.scope = scope

    def __call__(self, arg: P) -> R:
        return self.func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self.source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"


class Names(StrEnum):
    REF_ = auto()
    PC_FUNC_ = auto()
    ARG = auto()
    FUNC = auto()
    DUMMY = auto()
    PYCHAIN_AST = auto()


type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]
BUILTIN_NAMES = set(dir(builtins))
INLINEABLE_BUILTINS: set[type | Callable[..., Any]] = {
    int,
    str,
    float,
    list,
    dict,
    tuple,
    set,
    zip,
    enumerate,
    range,
    map,
    filter,
    reversed,
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
    iter,
    next,
}
