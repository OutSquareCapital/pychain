import ast
from collections.abc import Callable
from typing import Any, Literal
from ._scope import ScopeManager
from ._ast_parsers import get_func_name, get_module_ast, TypeTracker
from ._cythonizer import CythonCompiler

from ._module_builder import ModuleBuilder, SourceCode
from ._protocols import Func, Names, Operation

type CompileResult[T] = tuple[Callable[[T], Any], SourceCode]


class Compiler[P]:
    def __init__(self, pipeline: list[Operation[P, Any]], tracker: TypeTracker) -> None:
        self.pipeline = pipeline
        self.manager = ScopeManager()
        self.tracker = tracker

    def run(self, backend: Literal["python", "numba", "cython"]):
        compiled_func, source_code = self._compile_logic()
        match backend:
            case "numba":
                from numba import jit

                compiled_func: Callable[[P], Any] = jit(compiled_func)
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

    def _compile_logic(self) -> CompileResult[P]:
        final_expr_ast: ast.expr = self._build_from_pipeline()
        func_name = get_func_name(final_expr_ast)
        module_ast = get_module_ast(func_name, final_expr_ast)
        source_code = ast.unparse(module_ast)
        code_obj = compile(module_ast, filename=Names.PYCHAIN_AST.value, mode="exec")
        exec(code_obj, self.manager.scope)
        return self.manager.scope[func_name], SourceCode(source_code, func_name)

    def _build_from_pipeline(self) -> ast.expr:
        final_expr_ast: ast.expr = ast.Name(id=Names.ARG.value, ctx=ast.Load())
        for op in self.pipeline:
            final_expr_ast = self.manager.build_operation_ast(op, final_expr_ast)
        return final_expr_ast
