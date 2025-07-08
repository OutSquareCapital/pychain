import functools as ft
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import cytoolz as cz

import src.pychain._lazyfuncs as lf
from .core import AbstractChain
from .executors import Checker, Converter

if TYPE_CHECKING:
    from .implementations import DictChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseDictChain[K, V](AbstractChain[dict[K, V]]):
    @property
    def convert_values_to(self) -> Converter[V]:
        return Converter(_value=self.unwrap().values())

    @property
    def convert_keys_to(self) -> Converter[K]:
        return Converter(_value=self.unwrap().keys())

    @property
    def convert_items_to(self) -> Converter[tuple[K, V]]:
        return Converter(_value=self.unwrap().items())

    @property
    def check_if_values(self) -> Checker[V]:
        return Checker(_value=self.unwrap().values())

    @property
    def check_if_keys(self) -> Checker[K]:
        return Checker(_value=self.unwrap().keys())

    @property
    def check_if_items(self) -> Checker[tuple[K, V]]:
        return Checker(_value=self.unwrap().items())

    def into[K1, V1](
        self, f: lf.TransformFunc[dict[K, V], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return self.__class__(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def map_items[K1, V1](
        self,
        f: lf.TransformFunc[tuple[K, V], tuple[K1, V1]],
    ) -> "DictChain[K1, V1]":
        return self.into(f=ft.partial(cz.dicttoolz.itemmap, f))

    def map_keys[K1](self, f: lf.TransformFunc[K, K1]) -> "DictChain[K1, V]":
        return self.into(f=ft.partial(cz.dicttoolz.keymap, f))

    def map_values[V1](self, f: lf.TransformFunc[V, V1]) -> "DictChain[K, V1]":
        return self.into(f=ft.partial(cz.dicttoolz.valmap, f))

    def filter_items(self, predicate: lf.CheckFunc[tuple[K, V]]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.itemfilter, predicate=predicate))

    def filter_keys(self, predicate: lf.CheckFunc[K]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.keyfilter, predicate=predicate))

    def filter_values(self, predicate: lf.CheckFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.valfilter, predicate=predicate))

    def with_key(self, key: K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.assoc_in, keys=keys, value=value))

    def update_in(self, *keys: K, f: lf.ProcessFunc[V]) -> Self:
        return self.do(f=ft.partial(cz.dicttoolz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[K, V]) -> Self:
        return self.do(f=ft.partial(lf.merge, others=others))

    def merge_with(self, f: Callable[..., V], *others: dict[K, V]) -> Self:
        return self.do(f=ft.partial(lf.merge_with, f=f, others=others))

    def drop(self, *keys: K) -> Self:
        return self.do(f=ft.partial(lf.dissoc, keys=keys))
