import builtins
import textwrap
from collections.abc import Callable, Iterable
from enum import StrEnum, auto
from typing import Any, NamedTuple, Final, TypeGuard


class Signature(NamedTuple):
    params: dict[str, type]
    return_type: type


type Scope = dict[str, Any]
type SignaturesRegistery = dict[int, Signature]
type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]


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
    _is_pychain_func: Final[bool] = True

    def __init__(
        self,
        compiled_func: Callable[[P], R],
        source_code: str,
        scope: Scope,
        param_type: type,
        return_type: type,
    ):
        self.func = compiled_func
        self.source_code = source_code
        self.scope = scope
        self.param_type = param_type
        self.return_type = return_type

    def __call__(self, arg: P) -> R:
        return self.func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self.source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"


def check_func(obj: Any) -> TypeGuard[Func[Any, Any]]:
    return getattr(obj, "_is_pychain_func", False) is True


class Names(StrEnum):
    REF_ = auto()
    PC_FUNC_ = auto()
    ARG = auto()
    FUNC = auto()
    LAMBDA = "<lambda>"
    DUMMY = auto()
    PYCHAIN_AST = auto()
    CFUNC = "cython.cfunc"
    CCALL = "cython.ccall"


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


CYTHON_TYPES: dict[type, str] = {
    builtins.int: "cython.int",
    builtins.float: "cython.double",
    builtins.bool: "cython.bint",
    builtins.str: "str",
    builtins.list: "list",
    builtins.dict: "dict",
    builtins.set: "set",
    builtins.tuple: "tuple",
    object: "object",
}
