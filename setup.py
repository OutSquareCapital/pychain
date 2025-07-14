# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize  # type: ignore
import numpy

extensions = [
    Extension(
        "pychain._exprs._core",
        ["src/pychain/_exprs/_core.pyx"],
        include_dirs=[numpy.get_include()],
    ),
    Extension(
        "pychain._struct._struct",
        ["src/pychain/_struct/_struct.pyx"],
        include_dirs=[numpy.get_include()],
    ),
    Extension(
        "pychain._iter._iter",
        ["src/pychain/_iter/_iter.pyx"],
        include_dirs=[numpy.get_include()],
    ),
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),  # type: ignore
)
