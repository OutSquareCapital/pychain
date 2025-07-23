import builtins
from collections.abc import Callable, Iterable
from typing import Any

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

CYTHON_TYPES = {
    int: "int",
    float: "double",
    str: "str",
    bool: "bint",
    list: "list",
    dict: "dict",
    tuple: "tuple",
    set: "set",
}


def flatten_recursive[T](
    d: dict[Any, T], parent_key: str = "", sep: str = "."
) -> dict[str, T]:
    items: dict[str, T] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items
