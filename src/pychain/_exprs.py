from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from ._compilers import Compiler
from ._protocols import Operation, pipe_arg
from ._cythonifier import Func
from .funcs import Process, Transform
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BaseExpr[P, R](ABC):
    """
    Base class interface for creating business logic specific expressions.
    The base method `_do` is used to apply operations to the expression pipeline.
    The `collect` method compiles the pipeline into a `Func` object.
    Into is used to convert the expression into a specific type.
    _arg is for specifying the type of the argument of the destined Expression type.
    For example, if you want to implement a chainable expression that takes a dictionary,
    you can set `_arg` to `dict[KR, VR]` where `KR` is the key type and `VR` is the value type.
    _do will return you a new instance where the type is dict[KT, VT] where `KT` is the key type and `VT` is the value type.
    This allows you to chain operations on the expression, without losing argument, and return types.

    """

    _pipeline: list[Operation[Any, Any]]
    _compiler: Compiler = field(default_factory=Compiler)

    def _new(self, op: Operation[Any, Any]) -> Any:
        return self.__class__(self._pipeline + [op], self._compiler)

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    @abstractmethod
    def _do(self, f: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def into(self, obj: Any) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def _arg(self) -> Any:
        raise NotImplementedError

    def collect(self) -> Func[P, R]:
        return self._compiler.run(self._pipeline)


class Expr[P, R](BaseExpr[P, R]):
    @property
    def _arg(self):
        return pipe_arg(P)

    def _do[T](self, func: Callable[..., T], *args: Any, **kwargs: Any) -> "Expr[P, T]":
        op = Operation(func=func, args=args, kwargs=kwargs)
        return self._new(op)

    def compose(self, *fns: Process[R]):
        expr = self
        for f in fns:
            expr = expr._do(f, pipe_arg(R))
        return expr

    def into[T](self, obj: Transform[R, T]):
        return self._do(obj, self._arg)
