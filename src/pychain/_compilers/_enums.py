import builtins
from collections.abc import Callable
from enum import StrEnum, auto
from typing import Any


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
