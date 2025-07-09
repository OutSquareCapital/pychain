import operator
from collections.abc import Callable
from typing import Any

def truth() -> Callable[[Any], bool]:
    """
    Returns a function that checks truthiness.

    Example:
        >>> truth()([])
        False
    """

    return operator.truth


def is_none() -> Callable[[Any], bool]:
    """
    Returns a function that checks if input is None.

    Example:
        >>> is_none()(None)
        True
    """

    return operator.is_(None)  # type: ignore[return-value]


def is_in(value: Any) -> Callable[[Any], bool]:
    """
    Returns a function that checks if input is in a value.

    Example:
        >>> is_in([1, 2, 3])(2)
        True
    """

    return lambda x: operator.contains(value, x)


def is_not_in(value: Any) -> Callable[[Any], bool]:
    """
    Returns a function that checks if input is not in a value.

    Example:
        >>> is_not_in([1, 2, 3])(4)
        True
    """

    return lambda x: not operator.contains(value, x)


def is_not_none() -> Callable[[Any], bool]:
    """
    Returns a function that checks if input is not None.

    Example:
        >>> is_not_none()(5)
        True
    """

    return operator.is_not(None)  # type: ignore[return-value]


def eq[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks equality with a value.

    Example:
        >>> eq(5)(5)
        True
    """

    return lambda x: operator.eq(x, value)


def ne[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks inequality with a value.

    Example:
        >>> ne(5)(3)
        True
    """

    return lambda x: operator.ne(x, value)


def gt[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks if input is greater than a value.

    Example:
        >>> gt(3)(5)
        True
    """

    return lambda x: operator.gt(x, value)  # type: ignore[return-value]


def ge[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks if input is >= a value.

    Example:
        >>> ge(3)(3)
        True
    """

    return lambda x: operator.ge(x, value)  # type: ignore[return-value]


def lt[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks if input is < a value.

    Example:
        >>> lt(3)(2)
        True
    """

    return lambda x: operator.lt(x, value)  # type: ignore[return-value]


def le[T](value: T) -> Callable[[T], bool]:
    """
    Returns a function that checks if input is <= a value.

    Example:
        >>> le(3)(3)
        True
    """

    return lambda x: operator.le(x, value)  # type: ignore[return-value]
