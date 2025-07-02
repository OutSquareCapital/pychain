from dataclasses import dataclass
from collections.abc import Callable
import cytoolz as cz
from typing import Self


@dataclass(slots=True, frozen=True)
class DictStream[K, V]:
    _data: dict[K, V]

    def _new(self, data: dict[K, V]) -> Self:
        return self.__class__(data)

    def _transform[K1, V1](self, data: dict[K1, V1]) -> "DictStream[K1, V1]":
        return self.__class__(data)  # type: ignore

    def map_items[K1, V1](
        self, f: Callable[[tuple[K, V]], tuple[K1, V1]]
    ) -> "DictStream[K1, V1]":
        return self._transform(cz.dicttoolz.itemmap(f, self._data))

    def map_keys[K1](self, f: Callable[[K], K1]) -> "DictStream[K1, V]":
        return self._transform(cz.dicttoolz.keymap(f, self._data))

    def map_values[V1](self, f: Callable[[V], V1]) -> "DictStream[K, V1]":
        return self._transform(cz.dicttoolz.valmap(f, self._data))

    def assoc(self, key: K, value: V) -> Self:
        return self._new(cz.dicttoolz.assoc(self._data, key, value))

    def dissoc(self, *keys: K) -> Self:
        return self._new(cz.dicttoolz.dissoc(d=self._data, *keys))

    def filter_by_item(self, predicate: Callable[[tuple[K, V]], bool]) -> Self:
        return self._new(cz.dicttoolz.itemfilter(predicate, self._data))

    def filter_by_key(self, predicate: Callable[[K], bool]) -> Self:
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_by_value(self, predicate: Callable[[V], bool]) -> Self:
        return self._new(cz.dicttoolz.valfilter(predicate, self._data))

    def stack(self, *others: dict[K, V]) -> Self:
        return self._new(cz.dicttoolz.merge(self._data, *others))

    def collect(self) -> dict[K, V]:
        return self._data
