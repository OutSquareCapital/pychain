from collections.abc import Callable, Container
from typing import Any, Literal

class ChainableOp[P, R]:
    """
    Enables method chaining for functional-style operations on data.
    """
    def __call__(self, value: P) -> R:
        """
        Executes the pipeline with the provided input value.

        Example:
            >>> ChainableOp(lambda x: x + 1)(5)
            6
        """
        ...

    def into[T](self, obj: Callable[[R], T]) -> "ChainableOp[R, T]":
        """
        Transforms the pipeline's output using the provided callable.

        Example:
            >>> ChainableOp(lambda x: x + 1).into(str)(5)
            '6'
        """
        ...

    def attr(self, name: str) -> "ChainableOp[R, Any]":
        """
        Accesses an attribute of the pipeline's output.

        Example:
            >>> class Obj:
            ...     pass
            >>> obj = Obj()
            ... obj.attr = 42
            >>> ChainableOp(lambda x: x).attr("attr")(obj)
            42
        """
        ...

    def item(self, key: Any) -> "ChainableOp[R, Any]":
        """
        Accesses an item of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x)["key"]({"key": 42})
            42
        """
        ...
    def hint[T](self, dtype: T) -> "ChainableOp[R, T]":
        """
        Provides a type hint for the operation's output.

        Example:
            >>> ChainableOp(lambda x: x).hint(int)("42")
            42
        """
        ...
    def add(self, value: R) -> "ChainableOp[R, R]":
        """
        Adds a value to the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).add(5)(10)
            15
        """
        ...

    def sub(self, value: R) -> "ChainableOp[R, R]":
        """
        Subtracts a value from the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).sub(5)(10)
            5
        """
        ...

    def mul(self, value: R) -> "ChainableOp[R, R]":
        """
        Multiplies the pipeline's output by a value.

        Example:
            >>> ChainableOp(lambda x: x).mul(5)(10)
            50
        """
        ...

    def truediv(self, value: R) -> "ChainableOp[P, R]":
        """
        Divides the pipeline's output by a value (true division).

        Example:
            >>> ChainableOp(lambda x: x).truediv(2)(10)
            5.0
        """
        ...

    def floordiv(self, value: R) -> "ChainableOp[P, R]":
        """
        Divides the pipeline's output by a value (floor division).

        Example:
            >>> ChainableOp(lambda x: x).floordiv(3)(10)
            3
        """
        ...
    def sub_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Subtracts the pipeline's output from a value (reversed subtraction).

        Example:
            >>> ChainableOp(lambda x: x).sub_r(10)(5)
            5
        """
        ...

    def truediv_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Divides a value by the pipeline's output (reversed true division).

        Example:
            >>> ChainableOp(lambda x: x).truediv_r(10)(2)
            5.0
        """
        ...

    def floordiv_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Divides a value by the pipeline's output (reversed floor division).

        Example:
            >>> ChainableOp(lambda x: x).floordiv_r(10)(3)
            3
        """
        ...

    def mod(self, value: R) -> "ChainableOp[P, R]":
        """
        Computes the modulus of the pipeline's output by a value.

        Example:
            >>> ChainableOp(lambda x: x).mod(3)(10)
            1
        """
        ...

    def pow(self, value: R) -> "ChainableOp[P, R]":
        """
        Raises the pipeline's output to the power of a value.

        Example:
            >>> ChainableOp(lambda x: x).pow(2)(3)
            9
        """
        ...
    def neg(self) -> "ChainableOp[P, R]":
        """
        Negates the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).neg()(5)
            -5
        """
        ...

    def round_to(self, ndigits: int) -> "ChainableOp[P, float]":
        """
        Rounds the pipeline's output to the specified number of digits.

        Example:
            >>> ChainableOp(lambda x: x).round_to(2)(3.14159)
            3.14
        """
        ...

    def is_true(self) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is truthy.

        Example:
            >>> ChainableOp(lambda x: x).is_true()(1)
            True
        """
        ...

    def is_none(self) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is None.

        Example:
            >>> ChainableOp(lambda x: x).is_none()(None)
            True
        """
        ...

    def is_not_none(self) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is not None.

        Example:
            >>> ChainableOp(lambda x: x).is_not_none()(5)
            True
        """
        ...
    def is_in(self, values: Container[P]) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is in the provided container.

        Example:
            >>> ChainableOp(lambda x: x).is_in([1, 2, 3])(2)
            True
        """
        ...

    def is_not_in(self, values: Container[P]) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is not in the provided container.

        Example:
            >>> ChainableOp(lambda x: x).is_not_in([1, 2, 3])(4)
            True
        """
        ...

    def is_distinct(self) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output contains distinct elements.

        Example:
            >>> ChainableOp(lambda x: x).is_distinct()([1, 2, 3])
            True
        """
        ...

    def is_iterable(self) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is iterable.

        Example:
            >>> ChainableOp(lambda x: x).is_iterable()([1, 2, 3])
            True
        """
        ...

    def is_all(self) -> "ChainableOp[P, bool]":
        """
        Checks if all elements in the pipeline's output are truthy.

        Example:
            >>> ChainableOp(lambda x: x).is_all()([True, True, True])
            True
        """
        ...

    def is_any(self) -> "ChainableOp[P, bool]":
        """
        Checks if any element in the pipeline's output is truthy.

        Example:
            >>> ChainableOp(lambda x: x).is_any()([False, True, False])
            True
        """
        ...

    def eq(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is equal to the provided value.

        Example:
            >>> ChainableOp(lambda x: x).eq(5)(5)
            True
        """
        ...

    def ne(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is not equal to the provided value.

        Example:
            >>> ChainableOp(lambda x: x).ne(5)(3)
            True
        """
        ...

    def gt(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is greater than the provided value.

        Example:
            >>> ChainableOp(lambda x: x).gt(3)(5)
            True
        """
        ...

    def ge(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is greater than or equal to the provided value.

        Example:
            >>> ChainableOp(lambda x: x).ge(5)(5)
            True
        """
        ...

    def lt(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is less than the provided value.

        Example:
            >>> ChainableOp(lambda x: x).lt(5)(3)
            True
        """
        ...

    def le(self, value: P) -> "ChainableOp[P, bool]":
        """
        Checks if the pipeline's output is less than or equal to the provided value.

        Example:
            >>> ChainableOp(lambda x: x).le(5)(5)
            True
        """
        ...
    def mean(self) -> "ChainableOp[P, float]":
        """
        Computes the mean of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).mean()([1, 2, 3, 4])
            2.5
        """
        ...

    def median(self) -> "ChainableOp[P, float]":
        """
        Computes the median of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).median()([1, 2, 3, 4])
            2.5
        """
        ...

    def mode(self) -> "ChainableOp[P, P]":
        """
        Computes the mode of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).mode()([1, 2, 2, 3])
            2
        """
        ...

    def stdev(self) -> "ChainableOp[P, float]":
        """
        Computes the standard deviation of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).stdev()([1, 2, 3, 4])
            1.2909944487358056
        """
        ...

    def variance(self) -> "ChainableOp[P, float]":
        """
        Computes the variance of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).variance()([1, 2, 3, 4])
            1.6666666666666667
        """
        ...

    def pvariance(self) -> "ChainableOp[float, float]":
        """
        Computes the population variance of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).pvariance()([1, 2, 3, 4])
            1.25
        """
        ...

    def median_low(self) -> "ChainableOp[float, float]":
        """
        Computes the low median of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).median_low()([1, 2, 3, 4])
            2
        """
        ...

    def median_high(self) -> "ChainableOp[P, float]":
        """
        Computes the high median of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).median_high()([1, 2, 3, 4])
            3
        """
        ...

    def median_grouped(self) -> "ChainableOp[P, float]":
        """
        Computes the grouped median of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).median_grouped()([1, 2, 2, 3])
            2.0
        """
        ...

    def quantiles(
        self, n: int, method: Literal["inclusive", "exclusive"]
    ) -> "ChainableOp[P, float]":
        """
        Computes the quantiles of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).quantiles(4, method="exclusive")([1, 2, 3, 4])
            [1.75, 2.5, 3.25]
        """
        ...

    def min(self) -> "ChainableOp[P, P]":
        """
        Computes the minimum value of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).min()([1, 2, 3, 4])
            1
        """
        ...

    def max(self) -> "ChainableOp[P, P]":
        """
        Computes the maximum value of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).max()([1, 2, 3, 4])
            4
        """
        ...

    def sum(self) -> "ChainableOp[P, P]":
        """
        Computes the sum of the pipeline's output.

        Example:
            >>> ChainableOp(lambda x: x).sum()([1, 2, 3, 4])
            10
        """
        ...

class OpConstructor:
    """
    Constructs chainable operations for functional-style data processing.
    """
    def __call__(self) -> ChainableOp[Any, Any]: ...
