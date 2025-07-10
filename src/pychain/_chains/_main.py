from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import cytoolz as cz

from ._executors import BaseAggregator, BaseGetter
from ._interfaces import (
    AbstractChain,
    BaseDictChain,
    BaseIterChain,
)
from .._protocols import TransformFunc, AggFunc


@dataclass(slots=True, frozen=True, repr=False)
class ScalarChain[T](AbstractChain[T]):
    """
    Chain and transform single (scalar) values.
    """

    def into[T1](self, f: TransformFunc[T, T1]) -> "ScalarChain[T1]":
        """
        Transform the scalar value and return a new ScalarChain.

        Example:
            >>> ScalarChain(2).into(lambda x: x + 3).unwrap()
            5
        """
        return ScalarChain(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def into_iter(self, n: int) -> "IterChain[T]":
        """
        Repeat the scalar value n times as an IterChain.

        Example:
            >>> ScalarChain(1).into_iter(3).convert_to.list()
            [1, 1, 1]
        """
        return IterChain(_value=iter([self.unwrap()])).repeat(n=n)

    def into_dict(self, n: int) -> "DictChain[int, T]":
        """
        Create a DictChain with n keys, all mapped to the scalar value.

        Example:
            >>> ScalarChain("x").into_dict(2).unwrap()
            {0: 'x', 1: 'x'}
        """
        val: T = self.unwrap()
        return DictChain(_value={i: val for i in range(n)})

    def into_dict_iter[K](self, n: int, *keys: K) -> "DictChain[K, IterChain[T]]":
        """
        Map each key to an IterChain of the scalar value repeated n times.

        Example:
            >>> ScalarChain(1).into_dict_iter(2, "a", "b").unwrap()[
            ...     "a"
            ... ].convert_to.list()
            [1, 1]
        """
        val: IterChain[T] = self.into_iter(n=n)
        return DictChain(_value={k: val for k in keys})


@dataclass(slots=True, frozen=True)
class Getter[V](BaseGetter[V]):
    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> ScalarChain[V1]:
        return ScalarChain(_value=f(self._value))


@dataclass(slots=True, frozen=True)
class Aggregator[T](BaseAggregator[T]):
    def __call__(self, on: Callable[[Iterable[T]], Any]) -> ScalarChain[Any]:
        return ScalarChain(_value=on(self._value))


@dataclass(slots=True, frozen=True, repr=False)
class IterChain[V](BaseIterChain[V]):
    """
    Chain, transform, and aggregate iterables.
    """

    @property
    def get(self) -> Getter[V]:
        """
        Return a Getter for extracting from the iterable.

        Example:
            >>> IterChain([1, 2, 3]).get.first().unwrap()
            1
        """
        return Getter(_value=self.unwrap())

    @property
    def agg(self) -> Aggregator[V]:
        """
        Aggregate the iterable using a function.

        Example:
            >>> IterChain([1, 2, 3]).agg(sum).unwrap()
            6
        """
        return Aggregator(_value=self.unwrap())

    def into_dict(self) -> "DictChain[int, V]":
        """
        Convert the iterable into a DictChain with integer keys.

        Example:
            >>> IterChain(["a", "b"]).into_dict().unwrap()
            {0: 'a', 1: 'b'}
        """
        return DictChain(_value={i: v for i, v in enumerate(self.unwrap())})

    def into_dict_iter[K](self, n: int) -> "DictChain[int, IterChain[V]]":
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

    @property
    def get_key(self) -> Getter[K]:
        """
        Return a Getter for the dictionary's keys.

        Example:
            >>> DictChain({"a": 1}).get_key.first().unwrap()
            'a'
        """
        return Getter(_value=self.unwrap().keys())

    @property
    def get_value(self) -> Getter[V]:
        """
        Return a Getter for the dictionary's values.

        Example:
            >>> DictChain({"a": 1}).get_value.first().unwrap()
            1
        """
        return Getter(_value=self.unwrap().values())

    @property
    def get_item(self) -> Getter[tuple[K, V]]:
        """
        Return a Getter for the dictionary's items.

        Example:
            >>> DictChain({"a": 1}).get_item.first().unwrap()
            ('a', 1)
        """
        return Getter(_value=self.unwrap().items())

    def agg_keys[K1](self, on: AggFunc[K, K1]) -> ScalarChain[K1]:
        """
        Aggregate the dictionary's keys with a function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_keys(list).unwrap()
            ['a', 'b']
        """
        return ScalarChain(_value=on(self.unwrap().keys()))

    def agg_values[V1](self, on: AggFunc[V, V1]) -> ScalarChain[V1]:
        """
        Aggregate the dictionary's values with a function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_values(sum).unwrap()
            3
        """
        return ScalarChain(_value=on(self.unwrap().values()))

    def agg_items[V1](self, on: AggFunc[tuple[K, V], V1]) -> ScalarChain[V1]:
        """
        Aggregate the dictionary's items with a function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_items(len).unwrap()
            2
        """
        return ScalarChain(_value=on(self.unwrap().items()))

    def into_iter_keys(self) -> "IterChain[K]":
        """
        Convert the dictionary's keys into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).into_iter_keys().convert_to.list()
            ['a', 'b']
        """
        return IterChain(_value=self.unwrap().keys())

    def into_iter_values(self) -> IterChain[V]:
        """
        Convert the dictionary's values into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).into_iter_values().convert_to.list()
            [1, 2]
        """
        return IterChain(_value=self.unwrap().values())

    def into_iter_items(self) -> IterChain[tuple[K, V]]:
        """
        Convert the dictionary's items into an IterChain.

        Example:
            >>> DictChain({"a": 1, "b": 2}).into_iter_items().convert_to.list()
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
        return self.into_iter_items().flat_map(
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
