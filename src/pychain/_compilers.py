import ast
import uuid
from collections.abc import Callable
from typing import Any

from ._ast_parsers import ScopeManager
from ._protocols import Func, Operation
from .consts import Names

type CompileResult[T] = tuple[Callable[[T], Any], str]


def to_ast[P](pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
    manager = ScopeManager()
    compiled_func, source_code = _compile_logic(pipeline, manager)

    return Func(compiled_func, source_code, manager.scope)


def to_numba[P](pipeline: list[Operation[P, Any]]) -> Func[P, Any]:
    manager = ScopeManager()
    compiled_func, source_code = _compile_logic(pipeline, manager)
    try:
        from numba import jit

        compiled_func: Callable[[P], Any] = jit(compiled_func)
    except Exception as e:
        print(f"Failed to compile function: {e}")
    return Func(compiled_func, source_code, manager.scope)


def _compile_logic[P](
    pipeline: list[Operation[P, Any]], manager: ScopeManager
) -> CompileResult[P]:
    final_expr_ast: ast.expr = ast.Name(id=Names.ARG.value, ctx=ast.Load())

    for op in pipeline:
        final_expr_ast = manager.build_operation_ast(op, final_expr_ast)
    func_name = f"{Names.PC_FUNC_.value}{uuid.uuid4().hex}"
    func_args = ast.arguments(args=[ast.arg(arg=Names.ARG.value)], defaults=[])
    func_def = ast.FunctionDef(
        name=func_name,
        args=func_args,
        body=[ast.Return(value=final_expr_ast)],
        decorator_list=[],
    )
    module_ast = ast.fix_missing_locations(ast.Module(body=[func_def], type_ignores=[]))
    source_code = ast.unparse(module_ast)
    code_obj = compile(module_ast, filename=Names.PYCHAIN_AST.value, mode="exec")
    exec(code_obj, manager.scope)
    return manager.scope[func_name], source_code
