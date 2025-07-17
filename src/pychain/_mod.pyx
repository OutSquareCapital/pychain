# distutils: language=c++

from itertools import product, starmap, takewhile, dropwhile
import operator as opr
from collections.abc import Callable, Container, Iterable
from functools import partial
from random import Random
from typing import Any, TypeVar
import statistics as stats
import cytoolz.dicttoolz as dcz
import cytoolz.functoolz as ftz
import cytoolz.itertoolz as itz

from ._protocols import CheckFunc, ProcessFunc, TransformFunc

K = TypeVar("K")
K1 = TypeVar("K1")
V = TypeVar("V")
V1 = TypeVar("V1")
T = TypeVar("T")
R = TypeVar("R")
P = TypeVar("P")
"""
Implement callable boolean functions using operator module and cytoolz.
larger_than, smaller_than, and other comparison functions are using the reverse operation inside the function, 
This is due to the fact that the order of the chain will be reversed relative to the the order of arg.
We first give the second argument to the function, and then the first argument.
So for some functions, we need to reverse the order of the arguments.
greater_than, smaller_than, are good examples of this.
"""

cdef class StructConstructor:
    def __call__(self, ktype: type, vtype: type):
        return Struct([])


cdef class OpConstructor:
    def __call__(self, dtype: type):
        return Op([])


cdef class IterConstructor:
    def __call__(self, dtype: type):
        return Iter([])

op = OpConstructor()
it = IterConstructor()
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

    cpdef returns(self):
        return ftz.compose_left(*self._pipeline)

cdef class Op(BaseExpr):
    _pipeline: list[Callable[[Any], Any]]

    cpdef into(self, obj: Callable[[Any], Any]):
        return self._do(obj)

    cpdef or_(self, value: T):
        return self._do(partial(opr.or_, value))

    cpdef xor(self, value: T):
        return self._do(partial(opr.xor, value))

    cpdef add(self, value: Any):
        return self._do(partial(opr.add, value))

    def sub(self, value: Any):
        return self._do(lambda x: opr.sub(x, value))

    def truediv(self, value: Any):
        return self._do(lambda x: opr.truediv(x, value))

    def floordiv(self, value: Any):
        return self._do(lambda x: opr.floordiv(x, value))

    def mod(self, value: Any):
        return self._do(lambda x: opr.mod(x, value))

    def pow(self, value: Any):
        return self._do(lambda x: opr.pow(x, value))

    def is_not_in(self, values: Container[Any]):
        return self._do(lambda x: not opr.contains(values, x))
    cpdef abs(self):
        return self._do(opr.abs)

    cpdef not_(self):
        return self._do(opr.not_)

    cpdef and_(self, value: Callable[[Any], bool]):
        return self._do(partial(opr.and_, value))
    cpdef mul(self, value: T):
        return self._do(partial(opr.mul, value))

    cpdef sub_r(self, value: T):
        return self._do(partial(opr.sub, value))

    cpdef truediv_r(self, value: T):
        return self._do(partial(opr.truediv, value))

    cpdef floordiv_r(self, value: T):
        return self._do(partial(opr.floordiv, value))

    cpdef mod_r(self, value: T):
        return self._do(partial(opr.mod, value))

    cpdef pow_r(self, value: T):
        return self._do(partial(opr.pow, value))

    cpdef neg(self):
        return self._do(opr.neg)

    cpdef round_to(self, ndigits: int):
        return self._do(partial(round, ndigits=ndigits))

    cpdef is_true(self):
        return self._do(opr.truth)

    cpdef is_none(self):
        return self._do(partial(opr.is_, None))

    cpdef is_not_none(self):
        return self._do(partial(opr.is_not, None))

    cpdef is_in(self, values: Container[T]):
        return self._do(partial(opr.contains, values))

    cpdef is_iterable(self):
        return self._do(itz.isiterable)

    cpdef eq(self, value: T):
        return self._do(partial(opr.eq, value))

    cpdef ne(self, value: T):
        return self._do(partial(opr.ne, value))

    cpdef gt(self, value: Any):
        return self._do(partial(opr.lt, value))

    cpdef ge(self, value: Any):
        return self._do(partial(opr.le, value))

    cpdef lt(self, value: Any):
        return self._do(partial(opr.gt, value))

    cpdef le(self, value: Any):
        return self._do(partial(opr.ge, value))



cdef class Iter(BaseExpr):
    _pipeline: list[Callable[[Iterable[Any]], Any]]

    cpdef into(self, obj: Callable[[Iterable[Any]], Any]):
        return self._do(obj)

    cdef agg(self, f: Callable[[Iterable[V]], Any]):
        return Op([self._do(f).returns()])

    cpdef group_by(self, on: TransformFunc[V, Any]):
        return self._do(partial(itz.groupby, on))

    cpdef into_frequencies(self):
        return self._do(itz.frequencies)

    cpdef reduce_by(self, key: TransformFunc[V, K], binop: Callable[[V, V], V]):
        return self._do(partial(itz.reduceby, key=key, binop=binop))

    cpdef map(self, f: TransformFunc[V, Any]):
        return self._do(f=partial(map, f))  # type: ignore

    cpdef flat_map(self, f: TransformFunc[V, Iterable[Any]]):
        return self._do(f=partial(_flat_map, func=f))

    cpdef starmap(self, f: TransformFunc[V, Any]):
        return self._do(f=partial(starmap, f))  # type: ignore

    cpdef take_while(self, predicate: CheckFunc[V]):
        return self._do(f=partial(takewhile, predicate))  # type: ignore

    cpdef drop_while(self, predicate: CheckFunc[V]):
        return self._do(f=partial(dropwhile, predicate))  # type: ignore

    cpdef interpose(self, element: T):
        return self._do(f=partial(itz.interpose, element))

    cpdef top_n(self, n: int, key: Callable[[Any], Any] | None = None):
        return self._do(f=partial(itz.topk, n, key=key))

    cpdef random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(f=partial(itz.random_sample, probability, random_state=state))

    cpdef filter(self, f: CheckFunc[V]):
        return self._do(f=partial(filter, f))  # type: ignore

    cpdef accumulate(self, f: Callable[[V, V], V]):
        return self._do(f=partial(itz.accumulate, f))

    cpdef insert_left(self, value: T):
        return self._do(f=partial(itz.cons, value))

    cpdef peekn(self, n: int, note: str | None = None):
        return self._do(f=partial(_peekn, n=n, note=note))

    cpdef peek(self, note: str | None = None):
        return self._do(f=partial(_peek, note=note))

    cpdef head(self, n: int):
        return self._do(f=partial(itz.take, n))

    cpdef tail(self, n: int):
        return self._do(f=partial(itz.tail, n))

    cpdef drop_first(self, n: int):
        return self._do(f=partial(itz.drop, n))

    cpdef every(self, index: int):
        return self._do(f=partial(itz.take_nth, index))

    cpdef repeat(self, n: int):
        return self._do(f=partial(_repeat, n=n))

    cpdef unique(self):
        return self._do(f=itz.unique)

    cpdef cumsum(self):
        return self._do(f=partial(itz.accumulate, opr.add))

    cpdef cumprod(self):
        return self._do(f=partial(itz.accumulate, opr.mul))

    cpdef tap(self, func: Callable[[Any], None]):
        return self._do(f=partial(_tap, func=func))

    cpdef enumerate(self):
        return self._do(f=enumerate)

    cpdef flatten(self):
        return self._do(f=itz.concat)

    cpdef partition(self, n: int, pad: Any | None = None):
        return self._do(f=partial(itz.partition, n, pad=pad))

    cpdef partition_all(self, n: int):
        return self._do(f=partial(itz.partition_all, n))

    cpdef rolling(self, length: int):
        return self._do(f=partial(itz.sliding_window, length))

    cpdef cross_join(self, other: Iterable[Any]):
        return self._do(partial(product, other))

    cpdef diff(
        self,
        others: Iterable[Iterable[Any]],
        cpdefault: T | None = None,
        key: ProcessFunc[V] | None = None,
    ):

        return self._do(f=partial(_diff, others=others, ccpdefault=cpdefault, key=key))

    cpdef zip_with(self, others: Iterable[Iterable[Any]], strict: bool = False):
        return self._do(f=partial(_zip_with, others=others, strict=strict))

    cpdef merge_sorted(
        self,
        others: Iterable[Iterable[T]],
        sort_on: Callable[[Any], Any] | None = None,
    ):
        return self._do(f=partial(_merge_sorted, others=others, sort_on=sort_on))

    cpdef interleave(self, others: Iterable[Iterable[V]]):
        return self._do(f=partial(_interleave, others=others))

    cpdef concat(self, others: Iterable[Iterable[V]]):
        return self._do(f=partial(_concat, others=others))

    cpdef first(self):
        return self.agg(itz.first)

    cpdef second(self):
        return self.agg(itz.second)

    cpdef last(self):
        return self.agg(itz.last)

    cpdef length(self):
        return self.agg(itz.count)

    cpdef mean(self):
        return self.agg(stats.mean)

    cpdef median(self):
        return self.agg(stats.median)

    cpdef mode(self):
        return self.agg(stats.mode)

    cpdef stdev(self):
        return self.agg(stats.stdev)

    cpdef variance(self):
        return self.agg(stats.variance)

    cpdef pvariance(self):
        return self.agg(stats.pvariance)

    cpdef median_low(self):
        return self.agg(stats.median_low)

    cpdef median_high(self):
        return self.agg(stats.median_high)

    cpdef median_grouped(self):
        return self.agg(stats.median_grouped)

    cpdef sum(self):
        return self.agg(sum)

    cpdef min(self):
        return self.agg(min)

    cpdef max(self):
        return self.agg(max)

cdef class Struct(BaseExpr):
    _pipeline: list[Callable[[dict[Any, Any]], Any]]

    cpdef into(self, obj: Callable[[dict[Any, Any]], Any]):
        return self._do(obj)

    cpdef map_keys(self, f: TransformFunc[K, K1]):
        return self._do(f=partial(dcz.keymap, f))

    cpdef map_values(self, f: TransformFunc[V, V1]):
        return self._do(f=partial(dcz.valmap, f))

    cpdef select(self, predicate: CheckFunc[K]):
        return self._do(f=partial(dcz.keyfilter, predicate))

    cpdef filter(self, predicate: CheckFunc[V]):
        return self._do(f=partial(dcz.valfilter, predicate))

    cpdef filter_items(
        self,
        predicate: CheckFunc[tuple[Any, Any]],
    ):
        return self._do(partial(dcz.itemfilter, predicate))

    cpdef map_items(
        self,
        f: TransformFunc[tuple[Any, Any], tuple[Any, Any]],
    ):
        return self._do(partial(dcz.itemmap, f))

    cpdef with_key(self, key: Any, value: Any):
        return self._do(f=partial(dcz.assoc, key=key, value=value))

    cpdef with_nested_key(self, keys: Iterable[K] | K, value: Any):
        return self._do(f=partial(dcz.assoc_in, keys=keys, value=value))

    def flatten_keys(self):
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

        return self._do(f=partial(_flatten_recursive))

    cpdef update_in(self, keys: Iterable[Any], f: ProcessFunc[V]):
        return self._do(f=partial(dcz.update_in, keys=keys, func=f))

    cpdef merge(self, others: Iterable[dict[Any, Any]]):
        return self._do(f=partial(_merge, others=others))

    cpdef merge_with(self, f: Callable[[Any], Any], others: Iterable[dict[Any, Any]]):
        return self._do(f=partial(dcz.merge_with, f, *others))

    cpdef drop(self, keys: Iterable[Any]):
        return self._do(f=partial(_drop, keys=keys))

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
    return itz.concat(seqs=map(lambda x: [x] * n, value))

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

def _tap(value: Iterable[V], func: Callable[[V], None]):
    for item in value:
        func(item)
        yield item
