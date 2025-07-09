import operator
from collections.abc import Callable


def add[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that adds a value.

    Example:
        >>> add(2)(3)
        5
    """

    return lambda x: operator.add(x, value)


def sub[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that subtracts a value.

    Example:
        >>> sub(2)(5)
        3
    """

    return lambda x: operator.sub(x, value)


def mul[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that multiplies by a value.

    Example:
        >>> mul(3)(4)
        12
    """

    return lambda x: operator.mul(x, value)


def truediv[T](value: T) -> Callable[[T], T]:
    """
    Returns a function for true division by a value.

    Example:
        >>> truediv(2)(8)
        4.0
    """

    return lambda x: operator.truediv(x, value)


def floordiv[T](value: T) -> Callable[[T], T]:
    """
    Returns a function for floor division by a value.

    Example:
        >>> floordiv(3)(10)
        3
    """

    return lambda x: operator.floordiv(x, value)


def sub_r[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that subtracts input from a value.

    Example:
        >>> sub_r(10)(3)
        7
    """

    return lambda x: operator.sub(value, x)


def truediv_r[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that divides a value by input.

    Example:
        >>> truediv_r(10)(2)
        5.0
    """

    return lambda x: operator.truediv(value, x)


def mod[T](value: T) -> Callable[[T], T]:
    """
    Returns a function for modulo by a value.

    Example:
        >>> mod(4)(10)
        2
    """

    return lambda x: operator.mod(x, value)


def pow[T](value: T) -> Callable[[T], T]:
    """
    Returns a function for exponentiation by a value.

    Example:
        >>> pow(3)(2)
        8
    """

    return lambda x: operator.pow(x, value)


def floordiv_r[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that floor-divides a value by input.

    Example:
        >>> floordiv_r(10)(3)
        3
    """

    return lambda x: operator.floordiv(value, x)


def neg[T]() -> Callable[[T], T]:
    """
    Returns a function that negates its input.

    Example:
        >>> neg()(5)
        -5
    """

    return operator.neg  # type: ignore[return-value]
