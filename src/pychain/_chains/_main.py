from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import cytoolz as cz

from .._protocols import TransformFunc
from ._interfaces import (
    BaseDictChain,
    BaseIterChain,
)


@dataclass(slots=True, frozen=True, repr=False)
class IterChain[V](BaseIterChain[V]):
    """
    Chain, transform, and aggregate iterables.
    """

    def into_dict(self) -> "DictChain[int, V]":
        """
        Convert the iterable into a DictChain with integer keys.

        Example:
            >>> IterChain(["a", "b"]).into_dict().unwrap()
            {0: 'a', 1: 'b'}
        """
        return DictChain(_value={i: v for i, v in enumerate(self.unwrap())})

    def into_dict_iter(self, n: int) -> "DictChain[int, IterChain[V]]":
        """
        Map each integer key to this IterChain, n times.

        Example:
            >>> IterChain([1]).into_dict_iter(2).unwrap()[0].convert_to.list()
            [1]
        """
        return DictChain(_value={k: self for k in range(n)})

    def into_dict_iter_with_keys[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        """
        Map each provided key to this IterChain.

        Example:
            >>> IterChain([1]).into_dict_iter_with_keys("a", "b").unwrap()[
            ...     "a"
            ... ].convert_to.list()
            [1]
        """
        return DictChain(_value={k: self for k in keys})

    def into_groups[K](self, on: TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        """
        Group elements by a key function as IterChains.

        Example:
            >>> IterChain(["a", "bb", "c"]).into_groups(len).unwrap()[
            ...     2
            ... ].convert_to.list()
            ['bb']
        """
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self.unwrap())
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def into_reduced_groups[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        """
        Group by key and reduce each group with a binary operation.

        Examples:
            >>> IterChain(["bob", "cathy", "claude", "clara"]).into_reduced_groups(
            ...     key=lambda x: x.startswith("c"), binop=lambda x, y: x + " and " + y
            ... ).unwrap()
            {False: 'bob', True: 'cathy and claude and clara'}

        With numbers:
            >>> IterChain([1, 2, 3, 4, 5]).into_reduced_groups(
            ...     key=lambda x: x < 3, binop=lambda x, y: x + y
            ... ).unwrap()
            {True: 3, False: 12}
        """
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.unwrap()))

    def into_frequencies(self) -> "DictChain[V, int]":
        """
        Count the frequency of each element in the iterable.

        Example:
            >>> IterChain([1, 2, 2, 3]).into_frequencies().unwrap()
            {1: 1, 2: 2, 3: 1}
        """
        return DictChain(_value=cz.itertoolz.frequencies(self.unwrap()))

    def to_columns[T](
        self, column_extractors: dict[str, Callable[[V], T]]
    ) -> "DictChain[str, list[T]]":
        """
        Transforms a chain of records into a dictionary of columns (lists).

        Example:
            >>> from typing import NamedTuple
            >>> class Point(NamedTuple):
            ...     x: int
            ...     y: int
            >>> data = [Point(1, 2), Point(10, 20)]
            >>> IterChain(data).to_columns(
            ...     {"X_vals": lambda p: p.x, "Y_vals": lambda p: p.y}
            ... ).unwrap()
            {'X_vals': [1, 10], 'Y_vals': [2, 20]}
        """
        columns: dict[str, list[T]] = {name: [] for name in column_extractors.keys()}
        for item in self.unwrap():
            for name, extractor in column_extractors.items():
                columns[name].append(extractor(item))

        return DictChain(_value=columns)


@dataclass(slots=True, frozen=True, repr=False)
class DictChain[K, V](BaseDictChain[K, V]):
    """
    Chain, transform, and aggregate dictionaries.
    """
    def keys(self) -> "IterChain[K]":
        """
        Convert the dictionary's keys into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).keys().convert_to.list()
            ['a', 'b']
        """
        return IterChain(_value=self.unwrap().keys())

    def values(self) -> IterChain[V]:
        """
        Convert the dictionary's values into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).values().convert_to.list()
            [1, 2]
        """
        return IterChain(_value=self.unwrap().values())

    def items(self) -> IterChain[tuple[K, V]]:
        """
        Convert the dictionary's items into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).items().convert_to.list()
            [('a', 1), ('b', 2)]
        """
        return IterChain(_value=self.unwrap().items())

    def to_rows[R](self, row_factory: Callable[[K, V], Iterable[R]]) -> "IterChain[R]":
        """
        For each (key, value) pair, applies `row_factory` to produce an
        iterable of new values (rows), and flattens the results into a
        single chain of rows.

        This is a powerful method for unpivoting or restructuring dictionary data.

        Example:
            >>> data = {"A": [1, 2], "B": [3]}
            >>> DictChain(data).to_rows(
            ...     lambda key, values: [(key, val) for val in values]
            ... ).convert_to.list()
            [('A', 1), ('A', 2), ('B', 3)]
        """
        return self.items().flat_map(
            lambda pair: row_factory(pair[0], pair[1])
        )

    def unpivot[T](
        self,
        value_extractor: Callable[[V], Iterable[T]],
        key_name: str = "key",
        index_name: str = "index",
        value_name: str = "value",
    ) -> IterChain[dict[str, T]]:
        """
        Unpivots a dictionary of iterables into a chain of row-dictionaries.

        This is a high-level convenience function for common unpivoting tasks.
        For each key-value pair in the source dictionary, it generates multiple
        output rows.

        Each output row is a dictionary containing:
        - The original key.
        - The index of the value within the extracted iterable.
        - The value itself.

        Example:
            >>> data = {"A": "hi", "B": "world"}
            >>> DictChain(data).unpivot(
            ...     value_extractor=lambda s: list(s),  # extract characters
            ...     key_name="letter_group",
            ...     value_name="char",
            ... ).convert_to.list()
            [{'letter_group': 'A', 'index': 0, 'char': 'h'}, {'letter_group': 'A', 'index': 1, 'char': 'i'}, {'letter_group': 'B', 'index': 0, 'char': 'w'}, {'letter_group': 'B', 'index': 1, 'char': 'o'}, {'letter_group': 'B', 'index': 2, 'char': 'r'}, {'letter_group': 'B', 'index': 3, 'char': 'l'}, {'letter_group': 'B', 'index': 4, 'char': 'd'}]

        """

        def row_factory(key: K, container: V) -> Iterable[dict[str, Any]]:
            for i, value in enumerate(value_extractor(container)):
                yield {key_name: key, index_name: i, value_name: value}

        return self.to_rows(row_factory=row_factory)
