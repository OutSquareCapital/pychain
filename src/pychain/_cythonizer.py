import importlib.util
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._module_builder import SourceCode


def load_from_path(module_path: Path, func_name: str) -> Callable[..., Any]:
    module_name = module_path.stem.split(".")[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not create module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return getattr(module, func_name)


@dataclass(slots=True, frozen=True)
class CachePaths:
    hash: str
    base_dir: Path = Path.home() / ".pychain_cache"

    @property
    def build_dir(self) -> Path:
        return self.base_dir / self.hash

    @property
    def source_file(self) -> Path:
        return self.build_dir / f"{self.hash}.py"

    @property
    def setup_file(self) -> Path:
        return self.build_dir / "setup.py"

    def find_binary(self) -> Path | None:
        if binary := next(self.base_dir.glob(f"{self.hash}.*.pyd"), None):
            return binary
        return next(self.base_dir.glob(f"{self.hash}.*.so"), None)

    def find_binary_in_build_dir(self) -> Path:
        if binary := next(self.build_dir.glob(f"{self.hash}.*.pyd"), None):
            return binary
        if binary := next(self.build_dir.glob(f"{self.hash}.*.so"), None):
            return binary
        raise FileNotFoundError("Could not find compiled Cython binary in build dir.")


def run_process(command: list[str], cwd: Path) -> None:
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        print("INFO: Cython compilation successful.")
        return

    print("--- CYTHON BUILD FAILED ---")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    raise RuntimeError("Cython compilation failed.")


class CythonCompiler:
    def __init__(self, source: SourceCode):
        self.source = source
        self.paths = CachePaths(hash=source.get_hash())
        self.paths.base_dir.mkdir(exist_ok=True)

    def get_func(self) -> Callable[..., Any]:
        if binary_path := self.paths.find_binary():
            print(f"INFO: Found compiled binary in cache: {binary_path}")
            return load_from_path(binary_path, self.source.func_name)

        print("INFO: No compiled binary found in cache. Starting build process...")
        final_binary_path = self._compile()
        return load_from_path(final_binary_path, self.source.func_name)

    def _compile(self) -> Path:
        self._write_build_files()

        command = [sys.executable, "setup.py", "build_ext", "--inplace"]
        run_process(command=command, cwd=self.paths.build_dir)

        compiled_binary = self.paths.find_binary_in_build_dir()
        final_binary_path = self.paths.base_dir / compiled_binary.name

        shutil.move(src=compiled_binary, dst=final_binary_path)

        print(f"INFO: Cleaning up build directory: {self.paths.build_dir}")
        shutil.rmtree(self.paths.build_dir)

        return final_binary_path

    def _write_build_files(self) -> None:
        self.paths.build_dir.mkdir(exist_ok=True)
        print(f"INFO: Writing source and setup file to: {self.paths.build_dir}")
        self.source.write_to_file(self.paths.source_file)
        self._create_setup_file()

    def _create_setup_file(self) -> None:
        setup_content = f"""
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("{self.paths.source_file.name}", language_level=3),
)
"""
        self.paths.setup_file.write_text(textwrap.dedent(setup_content.strip()))
