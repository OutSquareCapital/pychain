from collections.abc import Callable
from typing import Any, Literal

from ._ast_parsers import TypeTracker
from ._cythonizer import CythonCompiler
from ._module_builder import ModuleBuilder, SourceCode
from ._protocols import Func, Operation
from ._scope import ScopeManager

type CompileResult[T] = tuple[Callable[[T], Any], SourceCode]


class Compiler[P]:
    def __init__(self, pipeline: list[Operation[P, Any]], tracker: TypeTracker) -> None:
        self.pipeline = pipeline
        self.manager = ScopeManager()
        self.tracker = tracker

    def run(self, backend: Literal["python", "cython"]):
        compiled_func, source_code = self.manager.build(self.pipeline)
        match backend:
            case "cython":
                source_code = ModuleBuilder(
                    signatures=self.tracker.inferred_signatures
                ).generate(source_code, self.manager.scope)
                compiled_func = CythonCompiler(source_code).get_func()
            case _:
                compiled_func: Callable[[P], Any] = compiled_func
        return Func(
            compiled_func,
            source_code.code,
            self.manager.scope,
            self.tracker.p_type,
            self.tracker.r_type,
        )
