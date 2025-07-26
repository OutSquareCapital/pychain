import ast
from collections.abc import Callable
from typing import Any, Literal

from ._ast_parsers import ScopeManager, get_func_name, get_module_ast
from ._cythonizer import CythonCompiler

from ._module_builder import ModuleBuilder, SourceCode
from ._protocols import Func, Names, Operation

type CompileResult[T] = tuple[Callable[[T], Any], SourceCode]


class Compiler[P]:
    def __init__(self, pipeline: list[Operation[P, Any]]) -> None:
        self.pipeline = pipeline
        self.manager = ScopeManager()

    def run(self, backend: Literal["python", "numba", "cython"]):
        compiled_func, source_code = self._compile_logic()
        match backend:
            case "numba":
                from numba import jit

                compiled_func: Callable[[P], Any] = jit(compiled_func)
            case "cython":
                _, temp_source_code = self._compile_logic()
                cython_source = ModuleBuilder().generate(
                    temp_source_code, self.manager.scope
                )
                loaded_func = CythonCompiler(cython_source).get_func()
                return Func(loaded_func, cython_source.code, self.manager.scope)

            case _:
                compiled_func: Callable[[P], Any] = compiled_func
        return Func(compiled_func, source_code.code, self.manager.scope)

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
