from itertools import product, starmap, takewhile, dropwhile
from collections.abc import Callable, Iterable
from random import Random
from typing import Any, TypeVar
import cytoolz.dicttoolz as dcz
import cytoolz.itertoolz as itz
import functools as ft
from ._protocols import CheckFunc, ProcessFunc, TransformFunc
from copy import deepcopy
from ._compilers import collect_ast, collect_scope
from ._func import Func
from ._obj_exprs import ObjExpr

K = TypeVar("K")
K1 = TypeVar("K1")
V = TypeVar("V")
V1 = TypeVar("V1")
T = TypeVar("T")
R = TypeVar("R")
P = TypeVar("P")

def collect_pipeline(pipeline: list[Callable[[P], Any]]) -> Callable[[P], Any]:
        try:
            compiled_func, source_code = collect_ast(pipeline)
        except Exception as e:
            print(f"Error collecting AST: {e}")
            compiled_func, source_code = collect_scope(pipeline)
        return Func(compiled_func, source_code)

cdef class StructConstructor:
    def __call__(self, ktype: type, vtype: type):
        return Struct([])


cdef class ExprConstructor:
    def __call__(self, dtype: type):
        return Expr([])


cdef class IterConstructor:
    def __call__(self, dtype: type):
        return Iter([])

expr = ExprConstructor()
iter = IterConstructor()
struct = StructConstructor()

cdef class BaseExpr:
    _pipeline: list[Callable[[Any], Any]]

    def __init__(self, pipeline: list[Callable[[Any], Any]]):
        self._pipeline = pipeline

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    def __class_getitem__(cls, key: tuple[type, ...]) -> type:
        return cls

    def _do(self, f: Callable[[Any], Any]):
        self._pipeline.append(f)
        return self

    cpdef _convert(self):
        return self._pipeline

    def into_partial(self, f: Callable[[Any], Any], *args: Any, **kwargs: Any):
        return self._do(ft.partial(f, *args, **kwargs))

    cpdef compose(self, ops: Iterable[Callable[[T], T]]):
        for op in ops:
            self._pipeline.append(op)
        return self

    cpdef collect(self):
        return collect_pipeline(self._pipeline)

    cpdef clone(self):
        return self._do(deepcopy)

cdef class Expr(BaseExpr):
    _pipeline: list[Callable[[Any], Any]]

    cpdef into(self, obj: Callable[[Any], Any]):
        return self._do(obj)

    cpdef into_expr(self, obj: ObjExpr):
        return self._do(obj)

    def into_iter(self, f: Callable[[Any], Iterable[Any]]):
        self._do(f)
        return Iter([self.collect()])

    def into_iter_func(self, f: Callable[[Any], Any]):
        self._do(ft.partial(itz.iterate, f))
        return Iter([self.collect()])

    def into_iter_range(self, start: int, stop: int, step: int = 1):
        self._do(ft.partial(range, start, stop, step))
        return Iter([self.collect()])

cdef class Iter(BaseExpr):
    _pipeline: list[Callable[[Iterable[Any]], Any]]
    def map_compose(self, fns: Iterable[ProcessFunc[V]]):
        mapping_func = collect_pipeline(list(fns))
        return self._do(ft.partial(map, mapping_func)) # type: ignore

    cpdef into(self, obj: Callable[[Iterable[Any]], Iterable[Any]]):
        return self._do(obj)

    cpdef agg(self, f: Callable[[Iterable[V]], Any]):
        return Expr([self._do(f).collect()])

    cpdef is_distinct(self):
        return self._do(itz.isdistinct)
    
    cpdef is_all(self):
        return self._do(all)

    cpdef is_any(self):
        return self._do(any)

    cpdef to_dict(self):
        return self._do(iter_to_dict)

    cpdef group_by(self, on: TransformFunc[V, Any]):
        return self._do(ft.partial(itz.groupby, on))

    cpdef into_frequencies(self):
        return self._do(itz.frequencies)

    cpdef reduce_by(self, key: TransformFunc[V, K], binop: Callable[[V, V], V]):
        return self._do(ft.partial(itz.reduceby, key=key, binop=binop))

    cpdef map(self, f: TransformFunc[V, Any]):
        return self._do(f=ft.partial(map, f))  # type: ignore

    cpdef filter(self, f: CheckFunc[V]):
        return self._do(f=ft.partial(filter, f))  # type: ignore

    cpdef flat_map(self, f: TransformFunc[V, Iterable[Any]]):
        return self._do(f=ft.partial(_flat_map, func=f))

    cpdef starmap(self, f: TransformFunc[V, Any]):
        return self._do(f=ft.partial(starmap, f))  # type: ignore

    cpdef take_while(self, predicate: CheckFunc[V]):
        return self._do(f=ft.partial(takewhile, predicate))  # type: ignore

    cpdef drop_while(self, predicate: CheckFunc[V]):
        return self._do(f=ft.partial(dropwhile, predicate))  # type: ignore

    cpdef interpose(self, element: T):
        return self._do(f=ft.partial(itz.interpose, element))

    cpdef top_n(self, n: int, key: Callable[[Any], Any] | None = None):
        return self._do(f=ft.partial(itz.topk, n, key=key))

    cpdef random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(f=ft.partial(itz.random_sample, probability, random_state=state))

    cpdef accumulate(self, f: Callable[[V, V], V]):
        return self._do(f=ft.partial(itz.accumulate, f))

    cpdef reduce(self, f: Callable[[V, V], V], initial: Any | None = None):
        return self._do(f=ft.partial(ft.reduce, f, initial=initial))

    cpdef insert_left(self, value: T):
        return self._do(f=ft.partial(itz.cons, value))

    cpdef peekn(self, n: int, note: str | None = None):
        return self._do(f=ft.partial(_peekn, n=n, note=note))

    cpdef peek(self, note: str | None = None):
        return self._do(f=ft.partial(_peek, note=note))

    cpdef head(self, n: int):
        return self._do(f=ft.partial(itz.take, n))

    cpdef tail(self, n: int):
        return self._do(f=ft.partial(itz.tail, n))

    cpdef drop_first(self, n: int):
        return self._do(f=ft.partial(itz.drop, n))

    cpdef every(self, index: int):
        return self._do(f=ft.partial(itz.take_nth, index))

    cpdef repeat(self, n: int):
        return self._do(f=ft.partial(_repeat, n=n))

    cpdef unique(self):
        return self._do(f=itz.unique)

    cpdef tap(self, func: Callable[[Any], None]):
        return self._do(f=ft.partial(_tap, func=func))

    cpdef enumerate(self):
        return self._do(f=enumerate)

    cpdef flatten(self):
        return self._do(f=itz.concat)

    cpdef partition(self, n: int, pad: Any | None = None):
        return self._do(f=ft.partial(itz.partition, n, pad=pad))

    cpdef partition_all(self, n: int):
        return self._do(f=ft.partial(itz.partition_all, n))

    cpdef rolling(self, length: int):
        return self._do(f=ft.partial(itz.sliding_window, length))

    cpdef cross_join(self, other: Iterable[Any]):
        return self._do(ft.partial(product, other))

    cpdef diff(
        self,
        others: Iterable[Iterable[Any]],
        cpdefault: T | None = None,
        key: ProcessFunc[V] | None = None,
    ):

        return self._do(f=ft.partial(_diff, others=others, ccpdefault=cpdefault, key=key))

    cpdef zip_with(self, others: Iterable[Iterable[Any]], strict: bool = False):
        return self._do(f=ft.partial(_zip_with, others=others, strict=strict))

    cpdef merge_sorted(
        self,
        others: Iterable[Iterable[T]],
        sort_on: Callable[[Any], Any] | None = None,
    ):
        return self._do(f=ft.partial(_merge_sorted, others=others, sort_on=sort_on))

    cpdef interleave(self, others: Iterable[Iterable[V]]):
        return self._do(f=ft.partial(_interleave, others=others))

    cpdef concat(self, others: Iterable[Iterable[V]]):
        return self._do(f=ft.partial(_concat, others=others))

    cpdef first(self):
        return self.agg(itz.first)

    cpdef second(self):
        return self.agg(itz.second)

    cpdef last(self):
        return self.agg(itz.last)

    cpdef length(self):
        return self.agg(itz.count)

    cpdef at_index(self, index: int) :
        return self.agg(ft.partial(itz.nth, index))


cdef class Struct(BaseExpr):
    _pipeline: list[Callable[[dict[Any, Any]], Any]]

    cpdef map_keys(self, f: TransformFunc[K, K1]):
        return self._do(f=ft.partial(dcz.keymap, f))

    cpdef map_values(self, f: TransformFunc[V, V1]):
        return self._do(f=ft.partial(dcz.valmap, f))

    cpdef select(self, predicate: CheckFunc[K]):
        return self._do(f=ft.partial(dcz.keyfilter, predicate))

    cpdef filter(self, predicate: CheckFunc[V]):
        return self._do(f=ft.partial(dcz.valfilter, predicate))

    cpdef filter_items(
        self,
        predicate: CheckFunc[tuple[Any, Any]],
    ):
        return self._do(ft.partial(dcz.itemfilter, predicate))

    cpdef map_items(
        self,
        f: TransformFunc[tuple[Any, Any], tuple[Any, Any]],
    ):
        return self._do(ft.partial(dcz.itemmap, f))

    cpdef with_key(self, key: Any, value: Any):
        return self._do(f=ft.partial(dcz.assoc, key=key, value=value))

    cpdef with_nested_key(self, keys: Iterable[K] | K, value: Any):
        return self._do(f=ft.partial(dcz.assoc_in, keys=keys, value=value))

    def flatten_keys(self):
        return self._do(f=_flatten_recursive)

    cpdef update_in(self, keys: Iterable[Any], f: ProcessFunc[V]):
        return self._do(f=ft.partial(dcz.update_in, keys=keys, func=f))

    cpdef merge(self, others: Iterable[dict[Any, Any]]):
        return self._do(f=ft.partial(_merge, others=others))

    cpdef merge_with(self, f: Callable[[Any], Any], others: Iterable[dict[Any, Any]]):
        return self._do(f=ft.partial(dcz.merge_with, f, *others))

    cpdef drop(self, keys: Iterable[Any]):
        return self._do(f=ft.partial(_drop, keys=keys))

#--------------- funcs ----------------


cpdef _merge_sorted(
    on: Iterable[V],
    others: Iterable[Iterable[V]],
    sort_on: Callable[[V], Any] | None = None,
):
    return itz.merge_sorted(on, *others, key=sort_on)

cpdef _concat(on: Iterable[V], others: Iterable[Iterable[V]]):
    return itz.concat([on, *others])
cpdef _drop(data: dict[K, Any], keys: Iterable[K]):
    return dcz.dissoc(data, *keys)

cpdef _flat_map(
    value: Iterable[V], func: TransformFunc[V, Iterable[V1]]
):
    return itz.concat(map(func, value))

cpdef _peekn(seq: Iterable[Any], n: int, note: str | None = None):
    values, sequence = itz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence

cpdef _peek(seq: Iterable[T], note: str | None = None):
    value, sequence = itz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence

def _repeat(value: Iterable[V], n: int) -> Iterable[V]:
    def fn(value: V) -> Iterable[V]:
        return [value] * n
    return itz.concat(seqs=map(fn, value))

cpdef _diff(
    value: Iterable[T],
    others: Iterable[Iterable[T]],
    ccpdefault: Any | None = None,
    key: ProcessFunc[V] | None = None,
):
    return itz.diff(*(value, *others), ccpdefault=ccpdefault, key=key)

cpdef _zip_with(
    value: Iterable[T], others: Iterable[Iterable[Any]], strict: bool
):
    return zip(value, *others, strict=strict)

cpdef _interleave(on: Iterable[V], others: Iterable[Iterable[V]]):
    return itz.interleave(seqs=[on, *others])

cpdef _merge(on: dict[K, V], others: Iterable[dict[K, V]]):
    return dcz.merge(on, *others)

cpdef iter_to_dict(value: Iterable[V]):
    return dict(enumerate(value))

def _tap(value: Iterable[V], func: Callable[[V], None]):
    for item in value:
        func(item)
        yield item

def _flatten_recursive(d: dict[Any, Any], parent_key: str = "", sep: str = "."):
    items: dict[str, Any] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(_flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items