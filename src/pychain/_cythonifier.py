import ast
import hashlib
import importlib.util
import inspect
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import appdirs  # type: ignore

from ._ast_parsers import FunctionDefFinder, LambdaFinder
from .funcs import CYTHON_TYPES

CACHE_DIR = Path(appdirs.user_cache_dir("pychain", "pychain_dev"))  # type: ignore
IN_MEMORY_CACHE: dict[str, Callable[..., Any]] = {}
CACHE_DIR.mkdir(parents=True, exist_ok=True)
#TODO: 
# - Check pk ca se recompile dans jupyter, ou en py file quand je relance
# - Mieux separer code 
# - Improve type inference

class Func[P, R]:
    def __init__(
        self, compiled_func: Callable[[P], R], source_code: str, scope: dict[str, Any]
    ):
        self.compiled_func = compiled_func
        self.source_code = source_code
        self.scope = scope

    def __call__(self, arg: P) -> R:
        return self.compiled_func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self.source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"

    def numbify(self) -> "Func[P, R]":
        from numba import jit

        try:
            compiled_func: Callable[[P], R] = jit(self.compiled_func)
        except Exception as e:
            print(f"Failed to compile function: {e}")
            return self
        return Func(compiled_func, self.source_code, self.scope)

    def cythonify(self, p_type: type | None = None, r_type: type | None = None):
        return Cythonifier(self).run(p_type, r_type)

    def extract(self) -> Callable[[P], R]:
        return self.compiled_func


class FuncRepr:
    def __init__(self):
        self.arg_name = "arg"
        self.body_expr = None

    def lambda_handler(self, module_ast: ast.Module):
        lambda_finder = LambdaFinder()
        lambda_finder.visit(module_ast)
        if lambda_node := lambda_finder.found_lambda:
            if len(lambda_node.args.args) == 1:
                self.arg_name = lambda_node.args.args[0].arg
                self.body_expr = lambda_node.body

    def function_def_handler(self, module_ast: ast.Module):
        def_finder = FunctionDefFinder()
        def_finder.visit(module_ast)
        if func_def_node := def_finder.found_func:
            if len(func_def_node.args.args) == 1 and isinstance(
                func_def_node.body[0], ast.Return
            ):
                self.arg_name = func_def_node.args.args[0].arg
                self.body_expr = func_def_node.body[0].value

    def pychain_handler(self, obj: Func[Any, Any]):
        func_ast = ast.parse(obj.source_code).body[0]
        if isinstance(func_ast, ast.FunctionDef):
            self.arg_name = func_ast.args.args[0].arg
            if isinstance(func_ast.body[0], ast.Return):
                self.body_expr = func_ast.body[0].value

    def create_deps_code(self, name: str) -> str | None:
        if self.body_expr:
            dep_func_code = textwrap.dedent(f"""
                    cdef object {name}(object {self.arg_name}):
                        return {ast.unparse(self.body_expr)}
                """)
            return dep_func_code
        return None


class Cythonifier[P, R]:
    def __init__(self, func: Func[P, R]) -> None:
        self.func = func

    def run(self, p_type: type | None = None, r_type: type | None = None) -> Func[P, R]:
        param_type = p_type or _infer_type(self.func.compiled_func, "P")
        return_type = r_type or _infer_type(self.func.compiled_func, "R")

        try:
            compiled_callable = self._get_or_compile(
                self.func.source_code, param_type, return_type
            )
            return Func(compiled_callable, self.func.source_code, self.func.scope)
        except Exception as e:
            print(f"Cython compilation failed: {e}\nFalling back to original function.")
            return self.func

    def _get_or_compile(
        self, source_code: str, p_type: type, r_type: type
    ) -> Callable[[P], R]:
        source_key = f"{source_code}|{p_type.__name__}|{r_type.__name__}"
        source_hash = hashlib.sha256(source_key.encode()).hexdigest()[:16]

        if cached_func := IN_MEMORY_CACHE.get(source_hash):
            return cached_func

        module_name = f"pc_{source_hash}"
        build_dir = CACHE_DIR / module_name

        try:
            compiled_func = self._load_module_from_dir(build_dir, module_name)
        except ModuleNotFoundError:
            build_dir.mkdir(exist_ok=True)
            pyx_code = _generate_pyx_code(source_code, p_type, r_type, self.func.scope)
            (build_dir / f"{module_name}.pyx").write_text(pyx_code, encoding="utf-8")

            setup_code = _generate_setup_code(module_name)
            _compile_extension(build_dir, setup_code)
            compiled_func = self._load_module_from_dir(build_dir, module_name)

        IN_MEMORY_CACHE[source_hash] = compiled_func
        return compiled_func

    def _load_module_from_dir(
        self, build_dir: Path, module_name: str
    ) -> Callable[[P], R]:
        if not build_dir.is_dir():
            raise ModuleNotFoundError(f"Build directory does not exist: {build_dir}")

        compiled_files = list(build_dir.rglob(f"{module_name}*.pyd")) + list(
            build_dir.rglob(f"{module_name}*.so")
        )
        if not compiled_files:
            raise ModuleNotFoundError(f"Could not find compiled module in {build_dir}")

        spec = importlib.util.spec_from_file_location(module_name, compiled_files[0])
        if not (spec and spec.loader):
            raise ModuleNotFoundError(
                f"Could not create module spec for '{compiled_files[0]}'."
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "cython_func")

def _infer_type(func: Callable[..., Any], type_var_name: str) -> type:
    try:
        sig = inspect.signature(func)
        match type_var_name:
            case "P" if sig.parameters:
                param = next(iter(sig.parameters.values()))
                if param.annotation is not inspect.Parameter.empty:
                    return param.annotation
            case "R" if sig.return_annotation is not inspect.Signature.empty:
                return sig.return_annotation
            case _:
                raise ValueError(f"Unknown type variable: {type_var_name}")
    except (ValueError, TypeError):
        pass
    return object


def _generate_pyx_code(
    source_code: str, p_type: type, r_type: type, scope: dict[str, Any]
) -> str:
    deps_code_list: list[str] = []
    processed_deps: set[str] = set()

    for name, obj in scope.items():
        if not name.startswith("ref_") or name in processed_deps:
            continue

        try:
            func_repr = FuncRepr()

            if isinstance(obj, Func):
                func_repr.pychain_handler(obj)  # type: ignore
            elif inspect.isfunction(obj):
                try:
                    func_source = textwrap.dedent(inspect.getsource(obj)).strip()
                except (OSError, TypeError):
                    continue
                parsable_source = func_source
                if parsable_source.startswith("."):
                    parsable_source = f"dummy{parsable_source}"

                try:
                    module_ast = ast.parse(parsable_source)
                except SyntaxError:
                    module_ast = ast.parse(f"_dummy = {parsable_source}")

                is_lambda = obj.__name__ == "<lambda>"

                if is_lambda:
                    func_repr.lambda_handler(module_ast)
                else:
                    func_repr.function_def_handler(module_ast)
            dep_func_code = func_repr.create_deps_code(name)
            if dep_func_code:
                deps_code_list.append(dep_func_code)
                processed_deps.add(name)

        except (TypeError, OSError, IndexError, SyntaxError):
            continue

    header = "# cython: language_level=3, cdivision=True"
    deps_code = "\n\n".join(deps_code_list)
    main_func_ast = ast.parse(source_code).body[0]
    if not (
        isinstance(main_func_ast, ast.FunctionDef)
        and isinstance(main_func_ast.body[0], ast.Return)
    ):
        raise ValueError(
            "Le code source principal doit être une fonction simple avec un seul return."
        )
    return_expr = main_func_ast.body[0].value
    if return_expr is None:
        raise ValueError("Le code source principal doit retourner une valeur.")
    return_expr_str = ast.unparse(return_expr)
    param_cython_type = CYTHON_TYPES.get(p_type, "object")
    return_cython_type = CYTHON_TYPES.get(r_type, "object")
    main_func_code = textwrap.dedent(f"""
        cpdef {return_cython_type} cython_func({param_cython_type} arg):
            return {return_expr_str}
    """)
    return "\n\n".join(filter(None, [header, deps_code, main_func_code]))


def _generate_setup_code(module_name: str) -> str:
    if sys.platform == "win32":
        compile_args = ["/O2"]
    else:
        compile_args = ["-O3"]

    return textwrap.dedent(f"""
        from setuptools import Extension, setup
        from Cython.Build import cythonize

        setup(
            ext_modules=cythonize([
                Extension(
                    name="{module_name}",
                    sources=["{module_name}.pyx"],
                    extra_compile_args={compile_args!r},
                )
            ])
        )
    """)


def _compile_extension(build_dir: Path, setup_code: str) -> None:
    (build_dir / "setup.py").write_text(setup_code, encoding="utf-8")
    last_error = None
    for attempt in range(3):
        result = subprocess.run(
            [sys.executable, "setup.py", "build_ext"],
            cwd=build_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return

        last_error = f"--- STDOUT ---\n{result.stdout}\n--- STDERR ---\n{result.stderr}"
        if "LNK1104" in result.stdout:
            print(f"Linker error (LNK1104). Retrying... (Attempt {attempt + 1}/3)")
            time.sleep(0.5)
        else:
            break

    raise RuntimeError(f"Build process failed.\n{last_error}")
