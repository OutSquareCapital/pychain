"""
dicttoolz
========

- assoc : Return a new dict with new key value pair
- assoc_in : Return a new dict with new, potentially nested, key value pair
- dissoc : Return a new dict with the given key(s) removed.
- get_in : Returns coll[i0][i1]...[iX] where [i0, i1, ..., iX]==keys.
- itemfilter : Filter items in dictionary by item
- itemmap : Apply function to items of dictionary
- keyfilter : Filter items in dictionary by key
- keymap : Apply function to keys of dictionary
- merge : Merge a collection of dictionaries
- merge_with : Merge dictionaries and apply function to combined values
- update_in : Update value in a (potentially) nested dictionary
- valfilter : Filter items in dictionary by value
- valmap : Apply function to values of dictionary
"""

from typing import Any
from collections.abc import Callable, Iterable

def assoc[KT, VT](
    d: dict[KT, VT], key: KT, value: VT, factory: Callable[[], dict[Any, Any]] = ...
) -> dict[KT, VT]: ...
def assoc_in[T](
    d: dict[Any, Any],
    keys: Iterable[Any],
    value: Any,
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[Any, Any]: ...
def dissoc[KT, VT](d: dict[KT, VT], *keys: KT, **kwargs: Any) -> dict[KT, VT]: ...
def get_in(
    keys: Iterable[Any], coll: Any, default: Any = ..., no_default: bool = ...
) -> Any: ...
def itemfilter[KT, VT](
    predicate: Callable[[tuple[KT, VT]], bool],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[KT, VT]: ...
def itemmap[KT, VT, T1, T2](
    func: Callable[[tuple[KT, VT]], tuple[T1, T2]],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[T1, T2]: ...
def keyfilter[KT, VT](
    predicate: Callable[[KT], bool],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[KT, VT]: ...
def keymap[KT, VT, T1](
    func: Callable[[KT], T1],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[T1, VT]: ...
def merge[KT, VT](*dicts: dict[KT, VT], **kwargs: Any) -> dict[KT, VT]: ...
def merge_with[KT, VT, T2](
    func: Callable[[list[VT]], T2], *dicts: dict[KT, VT], **kwargs: Any
) -> dict[KT, T2]: ...
def update_in[KT, VT](
    d: dict[Any, Any],
    keys: Iterable[Any],
    func: Callable[[Any], Any],
    default: Any = ...,
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[Any, Any]: ...
def valfilter[KT, VT](
    predicate: Callable[[VT], bool],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[KT, VT]: ...
def valmap[KT, VT, T2](
    func: Callable[[VT], T2],
    d: dict[KT, VT],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[KT, T2]: ...
