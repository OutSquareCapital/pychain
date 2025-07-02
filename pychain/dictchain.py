from collections.abc import Callable
from typing import Self
from dataclasses import dataclass
import cytoolz as cz


@dataclass(slots=True, frozen=True)
class DictChain[K, V]:
    value: dict[K, V]

    def _new(self, value: dict[K, V]) -> Self:
        return self.__class__(value)

    def _transform[K1, V1](self, value: dict[K1, V1]) -> "DictChain[K1, V1]":
        return self.__class__(value)  # type: ignore

    def map_items[K1, V1](
        self, f: Callable[[tuple[K, V]], tuple[K1, V1]]
    ) -> "DictChain[K1, V1]":
        return self._transform(value=cz.dicttoolz.itemmap(f, self.value))

    def map_keys[K1](self, f: Callable[[K], K1]) -> "DictChain[K1, V]":
        return self._transform(value=cz.dicttoolz.keymap(f, self.value))

    def map_values[V1](self, f: Callable[[V], V1]) -> "DictChain[K, V1]":
        return self._transform(value=cz.dicttoolz.valmap(f, self.value))

    def assoc(self, key: K, value: V) -> Self:
        return self._new(value=cz.dicttoolz.assoc(self.value, key, value))

    def dissoc(self, *keys: K) -> Self:
        return self._new(value=cz.dicttoolz.dissoc(d=self.value, *keys))

    def filter_by_item(self, predicate: Callable[[tuple[K, V]], bool]) -> Self:
        return self._new(value=cz.dicttoolz.itemfilter(predicate, self.value))

    def filter_by_key(self, predicate: Callable[[K], bool]) -> Self:
        return self._new(value=cz.dicttoolz.keyfilter(predicate, self.value))

    def filter_by_value(self, predicate: Callable[[V], bool]) -> Self:
        return self._new(value=cz.dicttoolz.valfilter(predicate, self.value))

    def stack(self, *others: dict[K, V]) -> Self:
        return self._new(value=cz.dicttoolz.merge(self.value, *others))

    def collect(self) -> dict[K, V]:
        return self.value
