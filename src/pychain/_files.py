import hashlib
import textwrap
from pathlib import Path


def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".pychain_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def get_source_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def manage_build_files(source: str) -> Path:
    source_hash = get_source_hash(source)
    build_dir = get_cache_dir() / source_hash
    build_dir.mkdir(exist_ok=True)
    source_file_path = build_dir / f"{source_hash}.py"
    if source_file_path.exists():
        print(f"INFO: Source file already exists in cache: {source_file_path}")
    else:
        print(f"INFO: New function detected. Writing source to: {source_file_path}")
        source_file_path.write_text(source, encoding="utf-8")
        _create_setup_file(source_file_path, build_dir)

    return source_file_path


def _create_setup_file(source_file: Path, build_dir: Path) -> None:
    setup_content = f"""
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("{source_file.name}"),
)
"""
    setup_path = build_dir / "setup.py"
    setup_path.write_text(textwrap.dedent(setup_content.strip()))
    print(f"INFO: Build file created at: {setup_path}")
    print(
        f"--> To compile manually, cd into '{build_dir}' and run: python setup.py build_ext --inplace"
    )
