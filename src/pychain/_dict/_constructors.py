from collections.abc import Iterable
from typing import Any

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
