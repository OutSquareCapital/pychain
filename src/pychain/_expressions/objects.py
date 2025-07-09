import operator
from collections.abc import Callable, Iterable
from typing import Any

def attr[T](*names: str) -> Callable[[T], T]:
    """
    Returns a function to get attribute(s) from an object.

    Example:
        >>> attr("real")(1 + 2j)
        1.0
    """

    return operator.attrgetter(*names)  # type: ignore[return-value]


def item[T](*keys: Any) -> Callable[[Iterable[T]], T]:
    """
    Returns a function to get item(s) from a collection.

    Example:
        >>> item(0)(["a", "b"])
        'a'
    """

    return operator.itemgetter(*keys)  # type: ignore[return-value]


def method[P](name: str, *args: P, **kwargs: P) -> Callable[[P], Any]:
    """
    Returns a function to call a method on an object.

    Example:
        >>> method("upper")("foo")
        'FOO'
    """

    return operator.methodcaller(name, *args, **kwargs)
