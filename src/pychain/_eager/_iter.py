from collections.abc import Callable, Iterable
from functools import reduce
from itertools import dropwhile, product, repeat, takewhile
from random import Random
from typing import Any, Concatenate

import cytoolz.itertoolz as itz

from . import _funcs as fn
from ._exprs import BasePipe, Pipe


class Iter[T](BasePipe[Iterable[T]]):
    def do[**P, R](
        self,
        func: Callable[Concatenate[Iterable[T], P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        return Iter(func(self.obj, *args, **kwargs))

    def map[**P, R](
        self, func: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
    ):
        return Iter(map(func, self.obj))

    def filter[**P](
        self, func: Callable[Concatenate[T, P], bool], *args: P.args, **kwargs: P.kwargs
    ):
        return Iter(filter(func, self.obj))

    def flat_map[R, **P](
        self,
        func: Callable[Concatenate[T, P], Iterable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        return Iter(itz.concat(map(func, self.obj, *args, **kwargs)))

    def take_while[**P](self, predicate: fn.Check[T]):
        return Iter(takewhile(predicate, self.obj))

    def drop_while[**P](self, predicate: fn.Check[T]):
        return Iter(dropwhile(predicate, self.obj))

    def agg[R, **P](
        self,
        f: Callable[Concatenate[Iterable[T], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        return Pipe(f(self.obj, *args, **kwargs))

    def group_by[K, **P](self, on: fn.Transform[T, K]):
        from ._struct import Struct

        return Struct(itz.groupby(on, self.obj))

    def into_frequencies(self):
        from ._struct import Struct

        return Struct(itz.frequencies(self.obj))

    def reduce_by[K](self, key: fn.Transform[T, K], binop: Callable[[T, T], T]):
        return Iter(itz.reduceby(key, binop, self.obj))

    def interpose(self, element: T):
        return Iter(itz.interpose(element, self.obj))

    def top_n(self, n: int, key: Callable[[T], Any] | None = None):
        return Iter(itz.topk(n, self.obj, key))

    def random_sample(self, probability: float, state: Random | int | None = None):
        return Iter(itz.random_sample(probability, self.obj, state))

    def accumulate(self, f: Callable[[T, T], T]):
        return Iter(itz.accumulate(f, self.obj))

    def reduce(self, func: Callable[[T, T], T]):
        return Pipe(reduce(func, self.obj))

    def insert_left(self, value: T):
        return Iter(itz.cons(value, self.obj))

    def peekn(self, n: int, note: str | None = None):
        return Iter(fn.peekn(self.obj, n, note))

    def peek(self, note: str | None = None):
        return Iter(fn.peek(self.obj, note))

    def head(self, n: int):
        return Iter(itz.take(n, self.obj))

    def tail(self, n: int):
        return Iter(itz.tail(n, self.obj))

    def drop_first(self, n: int):
        return Iter(itz.drop(n, self.obj))

    def every(self, index: int):
        return Iter(itz.take_nth(index, self.obj))

    def repeat(self, n: int):
        return Iter(repeat(self.obj, n))

    def unique(self):
        return Iter(itz.unique(self.obj))

    def tap(self, func: Callable[[T], None]):
        return Iter(fn.tap(self.obj, func))

    def enumerate(self):
        return Iter(enumerate(self.obj))

    def flatten(self):
        return Iter(itz.concat(self.obj))

    def partition(self, n: int, pad: T | None = None):
        return Iter(itz.partition(n, self.obj, pad))

    def partition_all(self, n: int):
        return Iter(itz.partition_all(n, self.obj))

    def rolling(self, length: int):
        return Iter(itz.sliding_window(length, self.obj))

    def cross_join(self, other: Iterable[T]):
        return Iter(product(self.obj, other))

    def diff(
        self,
        *others: Iterable[T],
        key: fn.Process[T] | None = None,
    ):
        return Iter(itz.diff(self.obj, *others, ccpdefault=None, key=key))

    def zip_with(self, *others: Iterable[T], strict: bool = False):
        return Iter(zip(self.obj, *others, strict=strict))

    def merge_sorted(
        self, *others: Iterable[T], sort_on: Callable[[T], Any] | None = None
    ):
        return Iter(itz.merge_sorted(self.obj, *others, key=sort_on))

    def interleave(self, *others: Iterable[T]):
        return Iter(itz.interleave((self.obj, *others)))

    def concat(self, *others: Iterable[T]):
        return Iter(itz.concat(self.obj, *others))

    def is_distinct(self):
        return Pipe(itz.isdistinct(self.obj))

    def is_all(self):
        return Pipe(all(self.obj))

    def is_any(self):
        return Pipe(any(self.obj))

    def to_dict(self):
        return Iter(dict(enumerate(self.obj)))

    def first(self):
        return self.agg(itz.first)

    def second(self):
        return self.agg(itz.second)

    def last(self):
        return self.agg(itz.last)

    def length(self):
        return self.agg(itz.count)

    def at_index(self, index: int):
        return Pipe(itz.nth(index, self.obj))
