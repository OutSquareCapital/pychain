from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from ._interfaces import BaseStruct, BaseIter
from .._protocols import TransformFunc
from .._fn import gp

@dataclass(slots=True, frozen=True, repr=False)
class Iter[V](BaseIter[V]):
    _value: Iterable[V]
    """
    A chain for working with iterables, allowing for transformations,
    aggregations, and other operations on the contained values.
    """

    def to_struct(self) -> "Struct[int, V]":
        return Struct(_value=self.to_dict())

    def group_by[K](self, on: TransformFunc[V, K]) -> "Struct[K, list[V]]":
        return Struct(_value=gp.group_by(on=on)(self.unwrap()))

    def reduce_by[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "Struct[K, V]":
        return Struct(_value=gp.reduce_by(key=key, binop=binop)(self.unwrap()))

    def into_frequencies(self) -> "Struct[V, int]":
        return Struct(_value=gp.frequencies(self.unwrap()))
@dataclass(slots=True, frozen=True, repr=False)
class Struct[K, V](BaseStruct[K, V]):
    """
    A chain for working with dictionaries, allowing for transformations,
    aggregations, and other operations on key-value pairs.
    """

    def iter_keys(self) -> Iter[K]:
        return Iter(_value=self.unwrap().keys())

    def iter_values(self) -> Iter[V]:
        return Iter(_value=self.unwrap().values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        return Iter(_value=self.unwrap().items())

    def unpivot[T](
        self,
        value_extractor: Callable[[V], Iterable[T]],
        key_name: str = "key",
        index_name: str = "index",
        value_name: str = "value",
    ) -> Iter[dict[str, T]]:
        """
        Unpivots a dictionary of iterables into a  of row-dictionaries.

        This is a high-level convenience function for common unpivoting tasks.
        For each key-value pair in the source dictionary, it generates multiple
        output rows.

        Each output row is a dictionary containing:
        - The original key.
        - The index of the value within the extracted iterable.
        - The value itself.

        Example:
            >>> data = {"A": "hi", "B": "world"}
            >>> Struct(data).unpivot(
            ...     value_extractor=lambda s: list(s),  # extract characters
            ...     key_name="letter_group",
            ...     value_name="char",
            ... ).to_list()
            [{'letter_group': 'A', 'index': 0, 'char': 'h'}, {'letter_group': 'A', 'index': 1, 'char': 'i'}, {'letter_group': 'B', 'index': 0, 'char': 'w'}, {'letter_group': 'B', 'index': 1, 'char': 'o'}, {'letter_group': 'B', 'index': 2, 'char': 'r'}, {'letter_group': 'B', 'index': 3, 'char': 'l'}, {'letter_group': 'B', 'index': 4, 'char': 'd'}]

        """

        def row_factory(key: K, container: V) -> Iterable[dict[str, Any]]:
            for i, value in enumerate(value_extractor(container)):
                yield {key_name: key, index_name: i, value_name: value}

        return self.iter_items().flat_map(lambda pair: row_factory(pair[0], pair[1]))