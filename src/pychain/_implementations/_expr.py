from __future__ import annotations

import inspect
from collections.abc import Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Self, TypeGuard

import cytoolz as cz

from .._executors import Executor

if TYPE_CHECKING:
    from ._dict import Dict
    from ._iter import Iter

type IntoExpr = str | Expr


class OpType(StrEnum):
    NAME = "__name__"
    LAMBDA = "lambda"
    CLASS = "__class__"
    EXPR = "Expr"
    IS_EXPR = "_is_pychain_expr"


def is_expr(obj: Any) -> TypeGuard[Expr]:
    return getattr(obj, OpType.IS_EXPR, False)


def parse_expr(expr: IntoExpr) -> Expr:
    match expr:
        case Expr():
            return expr
        case str():
            return key(expr)
        case _:
            raise TypeError(f"Expression must be of type str or Expr, not {type(expr)}")


def _parse_lambda(name: str, op: Callable[..., Any]) -> str:
    try:
        source = inspect.getsource(op).strip()
        if OpType.LAMBDA in source:
            lambda_part = source[source.find(OpType.LAMBDA) :].split(",")[0]
            if len(lambda_part) > 30:  # Truncate if too long
                lambda_part = lambda_part[:27] + "..."
            name = lambda_part
    except (OSError, TypeError):
        name = f"<{OpType.LAMBDA}>"
    finally:
        return name


def _op_name(op: Callable[..., Any]) -> str:
    if hasattr(op, OpType.NAME):
        name = op.__name__
        if name == f"<{OpType.LAMBDA}>":
            name = _parse_lambda(name, op)
    elif hasattr(op, OpType.CLASS):
        name = f"{op.__class__.__name__}"
    else:
        name = str(op)
    return name


class Expr(Executor[Any]):
    _input_name: str
    _output_name: str
    _is_pychain_expr = True
    _data: list[Callable[[Any], Any]]  # type: ignore[assignment]
    __slots__ = ("_data", "_input_name", "_output_name")  # type: ignore[assignment]

    def __init__(
        self, data: list[Callable[[Any], Any]], input_name: str, output_name: str
    ) -> None:
        self._input_name = input_name
        self._output_name = output_name
        super().__init__(data)

    def __repr__(self) -> str:
        """Return a string representation of the expression showing the execution plan."""
        ops_repr: list[str] = []
        for op in self.unwrap():
            ops_repr.append(_op_name(op))
        if ops_repr:
            pipeline = " -> ".join(ops_repr)
            return f"{OpType.EXPR}('{self._input_name}' -> {pipeline} -> '{self._output_name}')"
        else:
            return f"{OpType.EXPR}('{self._input_name}' -> '{self._output_name}')"

    def __call__(self, data: Any) -> Any:
        return self._func(data)

    @property
    def _func(self) -> Callable[[Any], Any]:
        return cz.functoolz.compose_left(*self.unwrap())

    def __compute__(self, input: dict[Any, Any], output: dict[Any, Any]) -> None:
        output[self._output_name] = self._func(input[self._input_name])

    def _new(self, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Self:
        return self.__class__(
            self._data + [func],
            self._input_name,
            self._output_name,
        )

    def into(self, func: Callable[[Any], Any]) -> Self:
        return self._new(func)

    def alias(self, name: str) -> Expr:
        self._output_name = name
        return self

    def field(self, name: str | int) -> Self:
        def operation(data: dict[Any, Any]) -> Any:
            try:
                return self._func(data).get(name)
            except (KeyError, IndexError, TypeError) as e:
                raise e.__class__(f"Clé ou index '{name}' invalide.") from e

        return self._new(operation)

    def apply(self, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Self:
        return self._new(func)

    def itr(self, func: Callable[[Iter[Any]], Any]) -> Self:
        from ._iter import Iter

        return self._new(lambda data: func(Iter(data)))

    def struct(self, func: Callable[[Dict[Any, Any]], Any]) -> Self:
        from ._dict import Dict

        return self._new(lambda data: func(Dict(data)))

    def add(self, value: Any) -> Self:
        return self._new(lambda x: x + value)

    def mul(self, value: Any) -> Self:
        return self._new(lambda x: x * value)

    def sub(self, value: Any) -> Self:
        return self._new(lambda x: x - value)

    def rsub(self, value: Any) -> Self:
        return self._new(lambda x: value - x)

    def truediv(self, value: Any) -> Self:
        return self._new(lambda x: x / value)

    def rtruediv(self, value: Any) -> Self:
        return self._new(lambda x: value / x)

    def floordiv(self, value: Any) -> Self:
        return self._new(lambda x: x // value)

    def rfloordiv(self, value: Any) -> Self:
        return self._new(lambda x: value // x)

    def mod(self, value: Any) -> Self:
        return self._new(lambda x: x % value)

    def pow(self, value: Any) -> Self:
        return self._new(lambda x: x**value)

    def neg(self) -> Self:
        return self._new(lambda x: -x)

    def pos(self) -> Self:
        return self._new(lambda x: +x)

    def abs(self) -> Self:
        return self._new(abs)

    def not_(self) -> Self:
        return self._new(lambda x: not x)

    def and_(self, value: Any) -> Self:
        return self._new(lambda x: x and value)

    def or_(self, value: Any) -> Self:
        return self._new(lambda x: x or value)

    def eq(self, value: Any) -> Self:
        return self._new(lambda x: x == value)

    def ne(self, value: Any) -> Self:
        return self._new(lambda x: x != value)

    def lt(self, value: Any) -> Self:
        return self._new(lambda x: x < value)

    def le(self, value: Any) -> Self:
        return self._new(lambda x: x <= value)

    def gt(self, value: Any) -> Self:
        return self._new(lambda x: x > value)

    def ge(self, value: Any) -> Self:
        return self._new(lambda x: x >= value)


class KeySelector:
    def __call__(self, name: str) -> Expr:
        return Expr([cz.functoolz.identity], name, name)

    def __get_attr__(self, name: str) -> Expr:
        return self(name)


def fn() -> Expr:
    return Expr([cz.functoolz.identity], "", "")


key = KeySelector()
