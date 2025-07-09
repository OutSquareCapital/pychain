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


def neg[T]() -> Callable[[T], T]:
    """
    Returns a function that negates its input.

    Example:
        >>> neg()(5)
        -5
    """

    return operator.neg  # type: ignore[return-value]


def truth() -> Callable[[Any], bool]:
    """
    Returns a function that checks truthiness.

    Example:
        >>> truth()([])
        False
    """

    return operator.truth


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


def rsub[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that subtracts input from a value.

    Example:
        >>> rsub(10)(3)
        7
    """

    return lambda x: operator.sub(value, x)


def rtruediv[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that divides a value by input.

    Example:
        >>> rtruediv(10)(2)
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


def rfloordiv[T](value: T) -> Callable[[T], T]:
    """
    Returns a function that floor-divides a value by input.

    Example:
        >>> rfloordiv(10)(3)
        3
    """

    return lambda x: operator.floordiv(value, x)
