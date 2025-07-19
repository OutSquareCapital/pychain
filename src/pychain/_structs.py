from collections.abc import Callable, Iterable
import cytoolz.dicttoolz as dcz
import functools as ft
from ._protocols import CheckFunc, ProcessFunc, TransformFunc
from ._exprs import BaseExpr
from ._func import flatten_recursive, merge, drop


class Struct[KP, VP, KR, VR](BaseExpr[dict[KP, VP], dict[KR, VR]]):
    __slots__ = "_pipeline"

    def _do[KT, VT](
        self, f: Callable[[dict[KR, VR]], dict[KT, VT]]
    ) -> "Struct[KP, VP, KR, VT]":
        return Struct(self._pipeline + [f])

    def map_keys[T](self, f: TransformFunc[KR, T]) -> "Struct[KP, VP, T, VR]":
        return self._do(f=ft.partial(dcz.keymap, f))  # type: ignore

    def map_values[T](self, f: TransformFunc[VR, T]) -> "Struct[KP, VP, KR, T]":
        return self._do(f=ft.partial(dcz.valmap, f))  # type: ignore

    def select(self, predicate: CheckFunc[KR]):
        return self._do(f=ft.partial(dcz.keyfilter, predicate))

    def filter(self, predicate: CheckFunc[VR]):
        return self._do(f=ft.partial(dcz.valfilter, predicate))

    def filter_items(
        self,
        predicate: CheckFunc[tuple[KR, VR]],
    ):
        return self._do(ft.partial(dcz.itemfilter, predicate))

    def map_items[KT, VT](
        self,
        f: TransformFunc[tuple[KR, VR], tuple[KT, VT]],
    ):
        return self._do(ft.partial(dcz.itemmap, f))

    def with_key(self, key: KR, value: VR):
        return self._do(f=ft.partial(dcz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KR] | KR, value: VR):
        return self._do(f=ft.partial(dcz.assoc_in, keys=keys, value=value))

    def flatten_keys(self) -> "Struct[KP, VP, str, VR]":
        return self._do(f=flatten_recursive)  # type: ignore

    def update_in(self, *keys: KR, f: ProcessFunc[VR]):
        return self._do(f=ft.partial(dcz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[KR, VR]):
        return self._do(f=ft.partial(merge, others=others))

    def merge_with(self, f: Callable[[Iterable[VR]], VR], *others: dict[KR, VR]):
        return self._do(f=ft.partial(dcz.merge_with, f, *others))

    def drop(self, *keys: KR):
        return self._do(f=ft.partial(drop, keys=keys))
