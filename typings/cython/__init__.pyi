import dataclasses as dataclasses
from builtins import (
    int as py_int,
    float as py_float,
    bool as py_bool,
    str as py_str,
    complex as py_complex,
)
from typing import Any, overload, Literal, Annotated
from types import TracebackType
from collections.abc import Iterable, Callable, Sequence
__version__: str

Py_UCS4 = py_int | str
Py_UNICODE = py_int | str

bint = py_bool
void = type[None]
basestring = py_str
unicode = py_str

compiled: bool

type _Decorator[C] = Callable[[C], C]

_func_deco: _Decorator[Any]

cfunc = ccall = compile = _func_deco

def locals(**kwargs: Any) -> _Decorator[Any]: ...
def _class_deco[T](__cls: T) -> T: ...

cclass = internal = c_api_binop_methods = type_version_tag = no_gc_clear = no_gc = (
    _class_deco
)

def returns[P, T](__type: type[T]) -> Callable[[Callable[P, object]], Callable[P, T]]: ...  # type: ignore
def exceptval(__val: Any, *, check: bool = False) -> _Decorator[Any]: ...

class _EmptyDecoratorAndManager(object):
    @overload
    def __call__(self, __val: bool) -> _Decorator[Any]: ...
    @overload
    def __call__[C](self, __func: C) -> C: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

_empty_decorator_and_manager: _EmptyDecoratorAndManager

@overload
def _compiler_directive[C](__func: C) -> C: ...
@overload
def _compiler_directive(__val: bool = ...) -> _Decorator[Any]: ...

binding = embedsignature = always_allow_keywords = unraisable_tracebacks = (
    cpp_locals
) = _compiler_directive

class _OverflowcheckClass:
    def __call__(self, __val: bool = ...) -> _Decorator[Any]: ...
    def fold(self, __val: bool = ...) -> _Decorator[Any]: ...

overflowcheck = _OverflowcheckClass()

class optimize:
    @staticmethod
    def use_switch(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def unpack_method_calls(__val: bool = ...) -> _Decorator[Any]: ...

class warn:
    @staticmethod
    def undeclared(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def unreachable(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def maybe_uninitialized(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def unused(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def unused_argument(__val: bool = ...) -> _Decorator[Any]: ...
    @staticmethod
    def multiple_declarators(__val: bool = ...) -> _Decorator[Any]: ...

@overload
def inline[C](__func: C) -> C: ...
@overload
def inline(
    __code: str,
    *,
    get_type: Callable[[object, object], str] = ...,
    lib_dir: str = ...,
    cython_include_dirs: Iterable[str] = ...,
    cython_compiler_directives: Iterable[str] = ...,
    force: bool = ...,
    quiet: bool = ...,
    locals: dict[str, str] = ...,
    globals: dict[str, str] = ...,
    language_level: str = ...,
) -> Any: ...
def cdiv(__a: int, __b: int) -> int: ...
def cmod(__a: int, __b: int) -> int: ...
@overload
def cast[T](__t: type[T], __value: Any) -> T: ...

# On Python 3.5, the latest version of Mypy available is 0.910 which doesn't understand ParamSpec
@overload
def cast[T, **P](__t: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T: ...
def sizeof(__obj: object) -> int: ...
def typeof(__obj: object) -> str: ...
def address(__obj: object) -> PointerType[Any]: ...

type const[T] = Annotated[T, "cython.const"]
type volatile[T] = Annotated[T, "cython.volatile"]

@overload
def declare[T](
    t: Callable[..., T],
    value: Any = ...,
) -> T: ...
@overload
def declare[T](
    t: Callable[..., T],
    *,
    visibility: Literal["public", "readonly", "private"] = ...,
) -> T: ...
@overload
def declare(**kwargs: type) -> None: ...

class _nogil:
    @overload
    def __call__(self, __val: bool) -> _Decorator[Any]: ...
    @overload
    def __call__[C](self, __func: C) -> C: ...
    @overload
    def __call__(self) -> "_nogil": ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

nogil = gil = _nogil

class _ArrayType[T]:
    is_array: bool
    subtypes: Sequence[str]
    dtype: T
    ndim: int
    is_c_contig: bool
    is_f_contig: bool
    inner_contig: bool
    broadcasting: Any

    # broadcasting is not used, so it's not clear about its type
    def __init__(
        self,
        dtype: T,
        ndim: int,
        is_c_contig: bool = ...,
        is_f_contig: bool = ...,
        inner_contig: bool = ...,
        broadcasting: Any = ...,
    ) -> None: ...
    def __repr__(self) -> str: ...

class CythonTypeObject(object): ...
class CythonType(CythonTypeObject): ...

class PointerType[T](CythonType):
    def __init__(
        self, value: ArrayType[T] | PointerType[T] | list[T] | int
    ) -> None: ...
    def __getitem__(self, ix: int) -> T: ...
    def __setitem__(self, ix: int, value: T) -> None: ...
    def __eq__(self, value: object) -> bool: ...
    def __repr__(self) -> str: ...

class ArrayType[T](PointerType[T]):
    def __init__(self) -> None: ...

def index_type[T](base_type: T, item: tuple[Any, ...] | slice | int) -> _ArrayType[T]: ...

class pointer[T](PointerType[T]):...
class array[T](ArrayType[T]):...

def struct(**members: type) -> type[Any]: ...
def union(**members: type) -> type[Any]: ...
def fused_type(*args: Any) -> type[Any]: ...

class typedef[T](CythonType):
    name: str

    def __init__(self, type: T, name: str| None = ...) -> None: ...
    def __call__(self, *arg: Any) -> T: ...
    def __repr__(self) -> str: ...
    __getitem__ = index_type

NULL: pointer[Any]

##### START: GENERATED LIST OF GENERATED TYPES #####
# Generated by "Tools/cython-generate-shadow-pyi.py" on 2024-09-24 11:45:22.474391

type const_bint = const[bint]
p_const_bint = pointer[const[bint]]
pp_const_bint = pointer[pointer[const[bint]]]
ppp_const_bint = pointer[pointer[pointer[const[bint]]]]
p_bint = pointer[bint]
pp_bint = pointer[pointer[bint]]
ppp_bint = pointer[pointer[pointer[bint]]]
type char = py_int
type const_char = const[py_int]
type p_const_char = pointer[const[py_int]]
pp_const_char = pointer[pointer[const[py_int]]]
ppp_const_char = pointer[pointer[pointer[const[py_int]]]]
p_char = pointer[py_int]
pp_char = pointer[pointer[py_int]]
ppp_char = pointer[pointer[pointer[py_int]]]
type complex = py_complex
type const_complex = const[py_complex]
p_const_complex = pointer[const[py_complex]]
pp_const_complex = pointer[pointer[const[py_complex]]]
ppp_const_complex = pointer[pointer[pointer[const[py_complex]]]]
p_complex = pointer[py_complex]
pp_complex = pointer[pointer[py_complex]]
ppp_complex = pointer[pointer[pointer[py_complex]]]
type double = py_float
type const_double = const[py_float]
p_const_double = pointer[const[py_float]]
pp_const_double = pointer[pointer[const[py_float]]]
ppp_const_double = pointer[pointer[pointer[const[py_float]]]]
p_double = pointer[py_float]
pp_double = pointer[pointer[py_float]]
ppp_double = pointer[pointer[pointer[py_float]]]
type doublecomplex = py_complex
type const_doublecomplex = const[py_complex]
p_const_doublecomplex = pointer[const[py_complex]]
pp_const_doublecomplex = pointer[pointer[const[py_complex]]]
ppp_const_doublecomplex = pointer[pointer[pointer[const[py_complex]]]]
p_doublecomplex = pointer[py_complex]
pp_doublecomplex = pointer[pointer[py_complex]]
ppp_doublecomplex = pointer[pointer[pointer[py_complex]]]
type float = py_float
type const_float = const[py_float]
p_const_float = pointer[const[py_float]]
pp_const_float = pointer[pointer[const[py_float]]]
ppp_const_float = pointer[pointer[pointer[const[py_float]]]]
p_float = pointer[py_float]
pp_float = pointer[pointer[py_float]]
ppp_float = pointer[pointer[pointer[py_float]]]
type floatcomplex = py_complex
type const_floatcomplex = const[py_complex]
p_const_floatcomplex = pointer[const[py_complex]]
pp_const_floatcomplex = pointer[pointer[const[py_complex]]]
ppp_const_floatcomplex = pointer[pointer[pointer[const[py_complex]]]]
p_floatcomplex = pointer[py_complex]
pp_floatcomplex = pointer[pointer[py_complex]]
ppp_floatcomplex = pointer[pointer[pointer[py_complex]]]
type int = py_int
type const_int = const[py_int]
p_const_int = pointer[const[py_int]]
pp_const_int = pointer[pointer[const[py_int]]]
ppp_const_int = pointer[pointer[pointer[const[py_int]]]]
p_int = pointer[py_int]
pp_int = pointer[pointer[py_int]]
ppp_int = pointer[pointer[pointer[py_int]]]
type long = py_int
type const_long = const[py_int]
p_const_long = pointer[const[py_int]]
pp_const_long = pointer[pointer[const[py_int]]]
ppp_const_long = pointer[pointer[pointer[const[py_int]]]]
p_long = pointer[py_int]
pp_long = pointer[pointer[py_int]]
ppp_long = pointer[pointer[pointer[py_int]]]
type py_long = py_int
type longdouble = py_float
type const_longdouble = const[py_float]
p_const_longdouble = pointer[const[py_float]]
pp_const_longdouble = pointer[pointer[const[py_float]]]
ppp_const_longdouble = pointer[pointer[pointer[const[py_float]]]]
p_longdouble = pointer[py_float]
pp_longdouble = pointer[pointer[py_float]]
ppp_longdouble = pointer[pointer[pointer[py_float]]]
type longdoublecomplex = py_complex
type const_longdoublecomplex = const[py_complex]
p_const_longdoublecomplex = pointer[const[py_complex]]
pp_const_longdoublecomplex = pointer[pointer[const[py_complex]]]
ppp_const_longdoublecomplex = pointer[pointer[pointer[const[py_complex]]]]
p_longdoublecomplex = pointer[py_complex]
pp_longdoublecomplex = pointer[pointer[py_complex]]
ppp_longdoublecomplex = pointer[pointer[pointer[py_complex]]]
type longlong = py_int
type const_longlong = const[py_int]
p_const_longlong = pointer[const[py_int]]
pp_const_longlong = pointer[pointer[const[py_int]]]
ppp_const_longlong = pointer[pointer[pointer[const[py_int]]]]
p_longlong = pointer[py_int]
pp_longlong = pointer[pointer[py_int]]
ppp_longlong = pointer[pointer[pointer[py_int]]]
type schar = py_int
type const_schar = const[py_int]
p_const_schar = pointer[const[py_int]]
pp_const_schar = pointer[pointer[const[py_int]]]
ppp_const_schar = pointer[pointer[pointer[const[py_int]]]]
p_schar = pointer[py_int]
pp_schar = pointer[pointer[py_int]]
ppp_schar = pointer[pointer[pointer[py_int]]]
type short = py_int
type const_short = const[py_int]
p_const_short = pointer[const[py_int]]
pp_const_short = pointer[pointer[const[py_int]]]
ppp_const_short = pointer[pointer[pointer[const[py_int]]]]
p_short = pointer[py_int]
pp_short = pointer[pointer[py_int]]
ppp_short = pointer[pointer[pointer[py_int]]]
type sint = py_int
type const_sint = const[py_int]
p_const_sint = pointer[const[py_int]]
pp_const_sint = pointer[pointer[const[py_int]]]
ppp_const_sint = pointer[pointer[pointer[const[py_int]]]]
p_sint = pointer[py_int]
pp_sint = pointer[pointer[py_int]]
ppp_sint = pointer[pointer[pointer[py_int]]]
type slong = py_int
type const_slong = const[py_int]
p_const_slong = pointer[const[py_int]]
pp_const_slong = pointer[pointer[const[py_int]]]
ppp_const_slong = pointer[pointer[pointer[const[py_int]]]]
p_slong = pointer[py_int]
pp_slong = pointer[pointer[py_int]]
ppp_slong = pointer[pointer[pointer[py_int]]]
type slonglong = py_int
type const_slonglong = const[py_int]
p_const_slonglong = pointer[const[py_int]]
pp_const_slonglong = pointer[pointer[const[py_int]]]
ppp_const_slonglong = pointer[pointer[pointer[const[py_int]]]]
p_slonglong = pointer[py_int]
pp_slonglong = pointer[pointer[py_int]]
ppp_slonglong = pointer[pointer[pointer[py_int]]]
type sshort = py_int
type const_sshort = const[py_int]
p_const_sshort = pointer[const[py_int]]
pp_const_sshort = pointer[pointer[const[py_int]]]
ppp_const_sshort = pointer[pointer[pointer[const[py_int]]]]
p_sshort = pointer[py_int]
pp_sshort = pointer[pointer[py_int]]
ppp_sshort = pointer[pointer[pointer[py_int]]]
type Py_hash_t = py_int
type constPy_hash_t = const[py_int]
p_constPy_hash_t = pointer[const[py_int]]
pp_constPy_hash_t = pointer[pointer[const[py_int]]]
ppp_constPy_hash_t = pointer[pointer[pointer[const[py_int]]]]
pPy_hash_t = pointer[py_int]
ppPy_hash_t = pointer[pointer[py_int]]
pppPy_hash_t = pointer[pointer[pointer[py_int]]]
type ptrdiff_t = py_int
type const_ptrdiff_t = const[py_int]
p_const_ptrdiff_t = pointer[const[py_int]]
pp_const_ptrdiff_t = pointer[pointer[const[py_int]]]
ppp_const_ptrdiff_t = pointer[pointer[pointer[const[py_int]]]]
p_ptrdiff_t = pointer[py_int]
pp_ptrdiff_t = pointer[pointer[py_int]]
ppp_ptrdiff_t = pointer[pointer[pointer[py_int]]]
type size_t = py_int
type const_size_t = const[py_int]
p_const_size_t = pointer[const[py_int]]
pp_const_size_t = pointer[pointer[const[py_int]]]
ppp_const_size_t = pointer[pointer[pointer[const[py_int]]]]
p_size_t = pointer[py_int]
pp_size_t = pointer[pointer[py_int]]
ppp_size_t = pointer[pointer[pointer[py_int]]]
type ssize_t = py_int
type const_ssize_t = const[py_int]
p_const_ssize_t = pointer[const[py_int]]
pp_const_ssize_t = pointer[pointer[const[py_int]]]
ppp_const_ssize_t = pointer[pointer[pointer[const[py_int]]]]
p_ssize_t = pointer[py_int]
pp_ssize_t = pointer[pointer[py_int]]
ppp_ssize_t = pointer[pointer[pointer[py_int]]]
type Py_ssize_t = py_int
type constPy_ssize_t = const[py_int]
p_constPy_ssize_t = pointer[const[py_int]]
pp_constPy_ssize_t = pointer[pointer[const[py_int]]]
ppp_constPy_ssize_t = pointer[pointer[pointer[const[py_int]]]]
pPy_ssize_t = pointer[py_int]
ppPy_ssize_t = pointer[pointer[py_int]]
pppPy_ssize_t = pointer[pointer[pointer[py_int]]]
type Py_tss_t = Any
type constPy_tss_t = const[Any]
pPy_tss_t = pointer[Any]
ppPy_tss_t = pointer[pointer[Any]]
pppPy_tss_t = pointer[pointer[pointer[Any]]]
type uchar = py_int
type const_uchar = const[py_int]
p_const_uchar = pointer[const[py_int]]
pp_const_uchar = pointer[pointer[const[py_int]]]
ppp_const_uchar = pointer[pointer[pointer[const[py_int]]]]
p_uchar = pointer[py_int]
pp_uchar = pointer[pointer[py_int]]
ppp_uchar = pointer[pointer[pointer[py_int]]]
type constPy_UCS4 = const[py_int]
p_constPy_UCS4 = pointer[const[py_int]]
pp_constPy_UCS4 = pointer[pointer[const[py_int]]]
ppp_constPy_UCS4 = pointer[pointer[pointer[const[py_int]]]]
pPy_UCS4 = pointer[py_int]
ppPy_UCS4 = pointer[pointer[py_int]]
pppPy_UCS4 = pointer[pointer[pointer[py_int]]]
type uint = py_int
type const_uint = const[py_int]
p_const_uint = pointer[const[py_int]]
pp_const_uint = pointer[pointer[const[py_int]]]
ppp_const_uint = pointer[pointer[pointer[const[py_int]]]]
p_uint = pointer[py_int]
pp_uint = pointer[pointer[py_int]]
ppp_uint = pointer[pointer[pointer[py_int]]]
type ulong = py_int
type const_ulong = const[py_int]
p_const_ulong = pointer[const[py_int]]
pp_const_ulong = pointer[pointer[const[py_int]]]
ppp_const_ulong = pointer[pointer[pointer[const[py_int]]]]
p_ulong = pointer[py_int]
pp_ulong = pointer[pointer[py_int]]
ppp_ulong = pointer[pointer[pointer[py_int]]]
type ulonglong = py_int
type const_ulonglong = const[py_int]
p_const_ulonglong = pointer[const[py_int]]
pp_const_ulonglong = pointer[pointer[const[py_int]]]
ppp_const_ulonglong = pointer[pointer[pointer[const[py_int]]]]
p_ulonglong = pointer[py_int]
pp_ulonglong = pointer[pointer[py_int]]
ppp_ulonglong = pointer[pointer[pointer[py_int]]]
type constPy_UNICODE = const[py_int]
p_constPy_UNICODE = pointer[const[py_int]]
pp_constPy_UNICODE = pointer[pointer[const[py_int]]]
ppp_constPy_UNICODE = pointer[pointer[pointer[const[py_int]]]]
pPy_UNICODE = pointer[py_int]
ppPy_UNICODE = pointer[pointer[py_int]]
pppPy_UNICODE = pointer[pointer[pointer[py_int]]]
type ushort = py_int
type const_ushort = const[py_int]
p_const_ushort = pointer[const[py_int]]
pp_const_ushort = pointer[pointer[const[py_int]]]
ppp_const_ushort = pointer[pointer[pointer[const[py_int]]]]
p_ushort = pointer[py_int]
pp_ushort = pointer[pointer[py_int]]
ppp_ushort = pointer[pointer[pointer[py_int]]]
type const_void = const[Any]
p_void = pointer[Any]
pp_void = pointer[pointer[Any]]
ppp_void = pointer[pointer[pointer[Any]]]

##### END: GENERATED LIST OF GENERATED TYPES #####
