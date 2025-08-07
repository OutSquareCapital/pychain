from collections.abc import Callable, Iterable
from typing import Concatenate

import cytoolz.dicttoolz as dcz

from . import _funcs as fn
from ._exprs import BasePipe


class Struct[KT, VT](BasePipe[dict[KT, VT]]):
    def do[KR, VR, **P](
        self,
        func: Callable[Concatenate[dict[KT, VT], P], dict[KR, VR]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        return Struct(func(self.obj, *args, **kwargs))

    def map_keys[T](self, f: fn.Transform[KT, T]):
        return Struct(dcz.keymap(f, self.obj))

    def map_values[T](self, f: fn.Transform[VT, T]):
        return Struct(dcz.valmap(f, self.obj))

    def flatten_keys(self):
        return Struct(fn.flatten_recursive(self.obj))

    def select(self, predicate: fn.Check[KT]):
        return Struct(dcz.keyfilter(predicate, self.obj))

    def filter(self, predicate: fn.Check[VT]):
        return Struct(dcz.valfilter(predicate, self.obj))

    def filter_items(
        self,
        predicate: fn.Check[tuple[KT, VT]],
    ):
        return Struct(dcz.itemfilter(predicate, self.obj))

    def map_items[KR, VR](
        self,
        f: fn.Transform[tuple[KT, VT], tuple[KR, VR]],
    ):
        return Struct(dcz.itemmap(f, self.obj))

    def with_key(self, key: KT, value: VT):
        return Struct(dcz.assoc(self.obj, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KT] | KT, value: VT):
        return Struct(dcz.assoc_in(self.obj, keys=keys, value=value))

    def update_in(self, *keys: KT, f: fn.Process[VT]):
        return Struct(dcz.update_in(self.obj, keys=keys, func=f))

    def merge(self, *others: dict[KT, VT]):
        return Struct(dcz.merge(self.obj, *others))

    def merge_with(self, f: Callable[[Iterable[VT]], VT], *others: dict[KT, VT]):
        return Struct(dcz.merge_with(f, self.obj, *others))

    def drop(self, *keys: KT):
        return Struct(dcz.dissoc(self.obj, *keys))
