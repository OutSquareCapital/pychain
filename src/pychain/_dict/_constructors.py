from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from .._core import SupportsKeysAndGetItem

if TYPE_CHECKING:
    from ._main import Dict


class DictConstructors:
    @staticmethod
    def from_zip[K, V](keys: Iterable[K], values: Iterable[V]) -> Dict[K, V]:
        """
        Create a Dict from two iterables of keys and values.

        Syntactic sugar for `Dict(dict(zip(keys, values)))`.

        >>> from pychain import Dict
        >>> Dict.from_zip([1, 2], ["a", "b"]).unwrap()
        {1: 'a', 2: 'b'}
        """
        from ._main import Dict

        return Dict(dict(zip(keys, values)))

    @staticmethod
    def from_object(obj: object) -> Dict[str, Any]:
        """
        Create a Dict from an object's __dict__ attribute.
        Syntactic sugar for `Dict(obj.__dict__)`.

        >>> from pychain import Dict
        >>> class A:
        ...     def __init__(self):
        ...         self.x = 1
        ...         self.y = 2
        >>> Dict.from_object(A()).unwrap()
        {'x': 1, 'y': 2}
        """
        from ._main import Dict

        return Dict(obj.__dict__)

    @staticmethod
    def from_[K, V](data: SupportsKeysAndGetItem[K, V]) -> Dict[K, V]:
        """
        Create a Dict from any mapping-like object.

        This is syntactic sugar for `Dict(dict(data))`, or `Dict({**data})`, and allows to use this function just like the built-in `dict()` constructor.

        Useful for TypedDicts, or other custom mapping-like objects.

        >>> from pychain import Dict
        >>> from typing import TypedDict
        >>> class TD(TypedDict):
        ...     a: int
        ...     b: str
        >>> td: TD = {"a": 1, "b": "x"}
        >>> Dict.from_(td).unwrap()
        {'a': 1, 'b': 'x'}
        """
        from ._main import Dict

        return Dict(dict(data))
