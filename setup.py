# setup.py
from pathlib import Path
from setuptools import setup, Extension
from Cython.Build import cythonize  # type: ignore[import]
import numpy
from enum import StrEnum, auto


class Builder(StrEnum):
    LANGUAGE_LEVEL = "3"
    CONVENTION = "_mod.pyx"
    SRC = auto()


def find_cython_extensions() -> list[Extension]:
    extensions: list[Extension] = []
    src_dir = Path(Builder.SRC)
    for pyx_file in src_dir.rglob(Builder.CONVENTION):
        module_path: Path = pyx_file.relative_to(src_dir).with_suffix("")
        module_name: str = ".".join(module_path.parts)
        src_code: str = str(pyx_file)
        extensions.append(
            Extension(
                name=module_name,
                sources=[src_code],
                include_dirs=[numpy.get_include()],
            )
        )

    return extensions


setup(
    ext_modules=cythonize(
        module_list=find_cython_extensions(),
        compiler_directives={"language_level": Builder.LANGUAGE_LEVEL},  # type: ignore
    ),
)
