from collections.abc import Iterable
from typing import Any

from .._protocols import SupportsKeysAndGetItem
from ._main import Dict


def dict_zip[K, V](keys: Iterable[K], values: Iterable[V]) -> Dict[K, V]:
    """
    Create a Dict from two iterables of keys and values.

    Syntactic sugar for `Dict(dict(zip(keys, values)))`.

    >>> dict_zip([1, 2], ["a", "b"])
    {1: 'a', 2: 'b'}
    """
    return Dict(dict(zip(keys, values)))


def dict_of(obj: object) -> Dict[str, Any]:
    """
    Create a Dict from an object's __dict__ attribute.
    Syntactic sugar for `Dict(obj.__dict__)`.

    >>> class A:
    ...     def __init__(self):
    ...         self.x = 1
    ...         self.y = 2
    >>> dict_of(A())
    {'x': 1, 'y': 2}
    """
    return Dict(obj.__dict__)


def dict_map[K, V](data: SupportsKeysAndGetItem[K, V]) -> Dict[K, V]:
    """
    Create a Dict from any mapping-like object.

    This is syntactic sugar for `Dict(dict(data))`, or `Dict({**data})`, and allows to use this function just like the built-in `dict()` constructor.

    Useful for TypedDicts, or other custom mapping-like objects.

    >>> from typing import TypedDict
    >>> class TD(TypedDict):
    ...     a: int
    ...     b: str
    >>> td: TD = {"a": 1, "b": "x"}
    >>> dict_map(td)
    {'a': 1, 'b': 'x'}
    """
    return Dict(dict(data))
