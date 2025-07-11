from collections.abc import Container
from dataclasses import dataclass
from typing import Any, Self

from .. import fn
from ._core import BaseChainableOp


@dataclass(slots=True, frozen=True)
class ChainableOp(BaseChainableOp):
    def attr(self, *names: str) -> Self:
        """
        Access attribute(s) of the input value.

        Example:
            >>> ChainableOp().attr("real")(3 + 4j)
            3.0
        """
        return self._chain(fn.attr(*names))

    def item(self, *keys: Any) -> Self:
        """
        Access item(s) of the input value using key(s).

        Example:
            >>> ChainableOp().item(0)([10, 20])
            10
        """
        return self._chain(fn.item(*keys))

    def method(self, name: str, *args: Any, **kwargs: Any) -> Self:
        """
        Call a method of the input value with given arguments.

        Example:
            >>> ChainableOp().method("upper")("abc")
            'ABC'
        """
        return self._chain(fn.method(name, *args, **kwargs))

    def add(self, value: Any) -> Self:
        """
        Add a value to the input.

        Example:
            >>> ChainableOp().add(5)(2)
            7
        """
        return self._chain(fn.add(value))

    def sub(self, value: Any) -> Self:
        """
        Subtract a value from the input.

        Example:
            >>> ChainableOp().sub(3)(10)
            7
        """
        return self._chain(fn.sub(value))

    def mul(self, value: Any) -> Self:
        """
        Multiply the input by a value.

        Example:
            >>> ChainableOp().mul(4)(3)
            12
        """
        return self._chain(fn.mul(value))

    def truediv(self, value: Any) -> Self:
        """
        Divide the input by a value (true division).

        Example:
            >>> ChainableOp().truediv(2)(8)
            4.0
        """
        return self._chain(fn.truediv(value))

    def floordiv(self, value: Any) -> Self:
        """
        Divide the input by a value (floor division).

        Example:
            >>> ChainableOp().floordiv(3)(10)
            3
        """
        return self._chain(fn.floordiv(value))

    def sub_r(self, value: Any) -> Self:
        """
        Subtract input from a value (reversed order).

        Example:
            >>> ChainableOp().sub_r(10)(3)
            7
        """
        return self._chain(fn.sub_r(value))

    def truediv_r(self, value: Any) -> Self:
        """
        Divide a value by the input (reversed order, true division).

        Example:
            >>> ChainableOp().truediv_r(8)(2)
            4.0
        """
        return self._chain(fn.truediv_r(value))

    def floordiv_r(self, value: Any) -> Self:
        """
        Divide a value by the input (reversed order, floor division).

        Example:
            >>> ChainableOp().floordiv_r(9)(2)
            4
        """
        return self._chain(fn.floordiv_r(value))

    def mod(self, value: Any) -> Self:
        """
        Modulo of input by a value.

        Example:
            >>> ChainableOp().mod(4)(10)
            2
        """
        return self._chain(fn.mod(value))

    def pow(self, value: Any) -> Self:
        """
        Raise input to the power of a value.

        Example:
            >>> ChainableOp().pow(3)(2)
            8
        """
        return self._chain(fn.pow(value))

    def neg(self) -> Self:
        """
        Negate the input value.

        Example:
            >>> ChainableOp().neg()(5)
            -5
        """
        return self._chain(fn.neg())

    def is_true(self) -> Self:
        """
        Test the truth value of the input.

        Example:
            >>> ChainableOp().is_true()([])
            False
        """
        return self._chain(fn.is_true())

    def is_none(self) -> Self:
        """
        Check if the input is None.

        Example:
            >>> ChainableOp().is_none()(5)
            False
        """
        return self._chain(fn.is_none())

    def is_not_none(self) -> Self:
        """
        Check if the input is not None.

        Example:
            >>> ChainableOp().is_not_none()(5)
            True
        """
        return self._chain(fn.is_not_none())

    def is_in(self, values: Container[Any]) -> Self:
        """
        Check if the input is in the given container.

        Example:
            >>> ChainableOp().is_in({1, 2, 3})(2)
            True
        """
        return self._chain(fn.is_in(values))

    def is_not_in(self, values: Container[Any]) -> Self:
        """
        Check if the input is not in the given container.

        Example:
            >>> ChainableOp().is_not_in({1, 2, 3})(4)
            True
        """
        return self._chain(fn.is_not_in(values))

    def is_distinct(self) -> Self:
        """
        Check if the input is distinct (not repeated).

        Example:
            >>> ChainableOp().is_distinct()([1, 2, 3])
            True
        """
        return self._chain(fn.is_distinct())

    def is_iterable(self) -> Self:
        """
        Check if the input is iterable.

        Example:
            >>> ChainableOp().is_iterable()([1, 2, 3])
            True
        """
        return self._chain(fn.is_iterable())

    def is_all(self) -> Self:
        """
        Check if all elements in the input iterable are truthy.

        Example:
            >>> ChainableOp().is_all()([1, 2, 3])
            True
        """
        return self._chain(fn.is_all())

    def is_any(self) -> Self:
        """
        Check if any element in the input iterable is truthy.

        Example:
            >>> ChainableOp().is_any()([0, 1, 2])
            True
        """
        return self._chain(fn.is_any())

    def eq(self, value: Any) -> Self:
        """
        Check if the input equals a value.

        Example:
            >>> ChainableOp().eq(5)(5)
            True
        """
        return self._chain(fn.eq(value))

    def ne(self, value: Any) -> Self:
        """
        Check if the input does not equal a value.

        Example:
            >>> ChainableOp().ne(5)(3)
            True
        """
        return self._chain(fn.ne(value))

    def gt(self, value: Any) -> Self:
        """
        Check if the input is greater than a value.

        Example:
            >>> ChainableOp().gt(2)(5)
            True
        """
        return self._chain(fn.gt(value))

    def ge(self, value: Any) -> Self:
        """
        Check if the input is greater than or equal to a value.

        Example:
            >>> ChainableOp().ge(2)(2)
            True
        """
        return self._chain(fn.ge(value))

    def lt(self, value: Any) -> Self:
        """
        Check if the input is less than a value.

        Example:
            >>> ChainableOp().lt(5)(3)
            True
        """
        return self._chain(fn.lt(value))

    def le(self, value: Any) -> Self:
        """
        Check if the input is less than or equal to a value.

        Example:
            >>> ChainableOp().le(5)(5)
            True
        """
        return self._chain(fn.le(value))
