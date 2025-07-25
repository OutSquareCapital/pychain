from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Literal

from ._compilers import to_ast, to_numba
from ._protocols import Operation, pipe_arg, Func
from .consts import Process, Transform


class BaseExpr[P, R](ABC):
    def __init__(self, pipeline: list[Operation[Any, Any]]) -> None:
        self._pipeline = pipeline

    def _new(self, op: Operation[Any, Any]) -> Any:
        return self.__class__(self._pipeline + [op])

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

    def collect(
        self, backend: Literal["python", "numba"] = "python"
    ) -> Func[P, R]:
        match backend:
            case "python":
                return to_ast(self._pipeline)
            case "numba":
                return to_numba(self._pipeline)


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
