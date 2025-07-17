
from collections.abc import Callable
from enum import IntEnum, auto
from typing import Any, NamedTuple
import operator as opr
from cytoolz.functoolz import compose_left
class OpType(IntEnum):
    ATTR = auto()
    CALL = auto()


class OpInfo(NamedTuple):
    type: OpType
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = {}


class Expression:
    def __init__(self, target_type: type) -> None:
        self._target_type: type = target_type
        self._operations: list[OpInfo] = []
        self._compiled_func: Callable[..., Any] | None = None

    def __getattr__(self, name: str):
        self._operations.append(OpInfo(type=OpType.ATTR, name=name))
        return self

    def __call__(self, *args: Any, **kwargs: Any):
        last_op_name: str = self._operations[-1].name
        new_op = OpInfo(
            type=OpType.CALL,
            name=last_op_name,
            args=args,
            kwargs=kwargs,
        )
        self._operations = self._operations[:-1] + [new_op]

        return self

    def compile(self) -> Callable[[Any], Any]:
        if self._compiled_func is None:
            op_funcs: list[Any] = []
            for op in self._operations:
                if op.type == OpType.ATTR:
                    op_funcs.append(opr.attrgetter(op.name))
                else:
                    op_funcs.append(opr.methodcaller(op.name, *op.args, **op.kwargs))
            all_steps: list[type] = [self._target_type] + op_funcs
            self._compiled_func = compose_left(*all_steps)

        return self._compiled_func

def expr(dtype: type):
    return Expression(target_type=dtype)

def as_expr[T](dtype: type[T]) -> T:
    """
    Wrap any class type, allowing you to use it in a chainable expression.
    This allow you to avoid lambdas and utilitary functions
    """
    ...

"""
    la func qui etait dans class op pyx
    cpdef into_expr(self, result: Expression):
        return result.compile()
"""