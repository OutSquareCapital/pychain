import functools as ft
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import cytoolz as cz

import pychain.lazyfuncs as lf
from pychain.core import BaseChain

if TYPE_CHECKING:
    from pychain.implementations import DictChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseDictChain[K, V](BaseChain[dict[K, V]]):
    def apply[K1, V1](
        self, f: Callable[[dict[K, V]], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        raise NotImplementedError

    def apply_map_items[K1, V1](
        self,
        f: lf.TransformFunc[tuple[K, V], tuple[K1, V1]],
    ) -> "DictChain[K1, V1]":
        return self.apply(f=ft.partial(cz.dicttoolz.itemmap, f))

    def apply_map_keys[K1](self, f: lf.TransformFunc[K, K1]) -> "DictChain[K1, V]":
        return self.apply(f=ft.partial(cz.dicttoolz.keymap, f))

    def apply_map_values[V1](self, f: lf.TransformFunc[V, V1]) -> "DictChain[K, V1]":
        return self.apply(f=ft.partial(cz.dicttoolz.valmap, f))

    def filter_items(self, predicate: lf.CheckFunc[tuple[K, V]]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.itemfilter, predicate=predicate))

    def filter_keys(self, predicate: lf.CheckFunc[K]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.keyfilter, predicate=predicate))

    def filter_values(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.valfilter, predicate=predicate))

    def map_items(self, f: lf.ProcessFunc[tuple[K, V]]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.itemmap, f))

    def map_keys(self, f: lf.TransformFunc[K, K]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.keymap, f))

    def map_values(self, f: lf.TransformFunc[V, V]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.valmap, f))

    def with_key(self, key: K, value: V) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.assoc_in, keys=keys, value=value))

    def update_in(self, *keys: K, f: lf.ProcessFunc[V]) -> Self:
        return self.lazy(f=ft.partial(cz.dicttoolz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[K, V]) -> Self:
        return self.lazy(f=ft.partial(lf.merge, others=others))

    def merge_with(self, f: Callable[..., V], *others: dict[K, V]) -> Self:
        return self.lazy(f=ft.partial(lf.merge_with, f=f, others=others))

    def drop(self, *keys: K) -> Self:
        return self.lazy(f=ft.partial(lf.dissoc, keys=keys))
