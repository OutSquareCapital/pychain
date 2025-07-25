from collections.abc import Callable, Iterable
from typing import Any

import cytoolz.dicttoolz as dcz

from ._exprs import BaseExpr
from ._protocols import get_placeholder, Operation, Transform, Check, Process


class Struct[KP, VP, KR, VR](BaseExpr[dict[KP, VP], dict[KR, VR]]):
    @property
    def _arg(self) -> dict[KR, VR]:
        return get_placeholder(dict[KR, VR])

    def _do[KT, VT, **P](
        self, f: Callable[P, dict[KT, VT]], *args: P.args, **kwargs: P.kwargs
    ) -> "Struct[KP, VP, KT, VT]":
        op = Operation(func=f, args=args, kwargs=kwargs)
        return self._new(op)

    def into[KT, VT](self, obj: Callable[[dict[KR, VR]], dict[KT, VT]]):
        return self._do(obj, self._arg)

    def map_keys[T](self, f: Transform[KR, T]):
        return self._do(dcz.keymap, f, self._arg)

    def map_values[T](self, f: Transform[VR, T]):
        return self._do(dcz.valmap, f, self._arg)

    def flatten_keys(self) -> "Struct[KP, VP, str, VR]":
        return self._do(flatten_recursive, self._arg)

    def select(self, predicate: Check[KR]):
        return self._do(dcz.keyfilter, predicate, self._arg)

    def filter(self, predicate: Check[VR]):
        return self._do(dcz.valfilter, predicate, self._arg)

    def filter_items(
        self,
        predicate: Check[tuple[KR, VR]],
    ):
        return self._do(dcz.itemfilter, predicate, self._arg)

    def map_items[KT, VT](
        self,
        f: Transform[tuple[KR, VR], tuple[KT, VT]],
    ):
        return self._do(dcz.itemmap, f, self._arg)

    def with_key(self, key: KR, value: VR):
        return self._do(dcz.assoc, self._arg, key=key, value=value)

    def with_nested_key(self, keys: Iterable[KR] | KR, value: VR):
        return self._do(dcz.assoc_in, self._arg, keys=keys, value=value)

    def update_in(self, *keys: KR, f: Process[VR]):
        return self._do(dcz.update_in, self._arg, keys=keys, func=f)

    def merge(self, *others: dict[KR, VR]):
        return self._do(dcz.merge, self._arg, *others)

    def merge_with(self, f: Callable[[Iterable[VR]], VR], *others: dict[KR, VR]):
        return self._do(dcz.merge_with, f, self._arg, *others)

    def drop(self, *keys: KR):
        return self._do(dcz.dissoc, self._arg, *keys)


def flatten_recursive[T](
    d: dict[Any, T], parent_key: str = "", sep: str = "."
) -> dict[str, T]:
    items: dict[str, T] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items
