from collections.abc import Callable, Iterable
from dataclasses import dataclass

import cytoolz as cz

from ._lazyfuncs import TransformFunc, AggFunc
from ._core import AbstractChain
from ._dict_base import BaseDictChain
from ._iter_base import BaseIterChain
from ._executors import GetterBase


@dataclass(slots=True, frozen=True)
class Getter[V](GetterBase[V]):
    """
    Getter extends GetterBase to extract elements or properties from an iterable and return them as ScalarChain.

    Example:
        >>> Getter([1, 2, 3]).first().unwrap()  # 1
        >>> Getter([1, 2, 3]).len().unwrap()  # 3
    """

    def __call__[V1](self, f: Callable[[Iterable[V]], V1]) -> "ScalarChain[V1]":
        """
        Apply a function to the iterable and return a ScalarChain of the result.

        Example:
            >>> Getter([1, 2, 3])(sum).unwrap()  # 6
        """
        return ScalarChain(_value=f(self._value))


@dataclass(slots=True, frozen=True, repr=False)
class ScalarChain[T](AbstractChain[T]):
    """
    ScalarChain enables chaining and transformation of single (scalar) values.

    Example:
        >>> ScalarChain(10).into(lambda x: x * 2).unwrap()  # 20
        >>> ScalarChain(5).into_iter(3).convert_to.list()  # [5, 5, 5]
    """

    def into[T1](self, f: TransformFunc[T, T1]) -> "ScalarChain[T1]":
        """
        Transform the scalar value using the provided function, returning a new ScalarChain.

        Example:
            >>> ScalarChain(2).into(lambda x: x + 3).unwrap()  # 5
        """
        return ScalarChain(
            _value=self._value,
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def into_iter(self, n: int) -> "IterChain[T]":
        """
        Create an IterChain by repeating the scalar value n times.

        Example:
            >>> ScalarChain(1).into_iter(3).convert_to.list()  # [1, 1, 1]
        """
        return IterChain(_value=iter([self.unwrap()])).repeat(n=n)

    def into_dict(self, n: int) -> "DictChain[int, T]":
        """
        Create a DictChain with n keys, all mapped to the scalar value.

        Example:
            >>> ScalarChain("x").into_dict(2).unwrap()  # {0: 'x', 1: 'x'}
        """
        val: T = self.unwrap()
        return DictChain(_value={i: val for i in range(n)})

    def into_dict_iter[K](self, n: int, *keys: K) -> "DictChain[K, IterChain[T]]":
        """
        Create a DictChain mapping each key to an IterChain of the scalar value repeated n times.

        Example:
            >>> ScalarChain(1).into_dict_iter(2, "a", "b").unwrap()[
            ...     "a"
            ... ].convert_to.list()  # [1, 1]
        """
        val: IterChain[T] = self.into_iter(n=n)
        return DictChain(_value={k: val for k in keys})


@dataclass(slots=True, frozen=True, repr=False)
class IterChain[V](BaseIterChain[V]):
    """
    IterChain enables chaining, transformation, and aggregation of iterables.

    Example:
        >>> IterChain([1, 2, 3]).map(lambda x: x * 2).convert_to.list()  # [2, 4, 6]
        >>> IterChain([1, 2, 2, 3]).into_frequencies().unwrap()  # {1: 1, 2: 2, 3: 1}
    """

    @property
    def get(self) -> Getter[V]:
        """
        Return a Getter for extracting elements or properties from the iterable.

        Example:
            >>> IterChain([1, 2, 3]).get.first().unwrap()  # 1
        """
        return Getter(_value=self.unwrap())

    def agg[V1](self, on: AggFunc[V, V1]) -> ScalarChain[V1]:
        """
        Aggregate the iterable using the provided aggregation function.

        Example:
            >>> IterChain([1, 2, 3]).agg(sum).unwrap()  # 6
        """
        return ScalarChain(_value=on(self.unwrap()))

    def into_dict(self) -> "DictChain[int, V]":
        """
        Convert the iterable into a DictChain with integer keys (enumerate).

        Example:
            >>> IterChain(["a", "b"]).into_dict().unwrap()  # {0: 'a', 1: 'b'}
        """
        return DictChain(_value={i: v for i, v in enumerate(self.unwrap())})

    def into_dict_iter[K](self, n: int) -> "DictChain[int, IterChain[V]]":
        """
        Create a DictChain mapping each integer key to this IterChain, n times.

        Example:
            >>> IterChain([1]).into_dict_iter(2).unwrap()[0].convert_to.list()  # [1]
        """
        return DictChain(_value={k: self for k in range(n)})

    def into_dict_iter_with_keys[K](self, *keys: K) -> "DictChain[K, IterChain[V]]":
        """
        Create a DictChain mapping each provided key to this IterChain.

        Example:
            >>> IterChain([1]).into_dict_iter_with_keys("a", "b").unwrap()[
            ...     "a"
            ... ].convert_to.list()  # [1]
        """
        return DictChain(_value={k: self for k in keys})

    def into_groups[K](self, on: TransformFunc[V, K]) -> "DictChain[K, IterChain[V]]":
        """
        Group elements by a key function, returning a DictChain of IterChains.

        Example:
            >>> IterChain(["a", "bb", "c"]).into_groups(len).unwrap()[
            ...     "2"
            ... ].convert_to.list()  # ['bb']
        """
        grouped: dict[K, list[V]] = cz.itertoolz.groupby(key=on, seq=self.unwrap())
        return DictChain(_value={k: IterChain(v) for k, v in grouped.items()})

    def into_reduced_groups[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "DictChain[K, V]":
        """
        Group elements by a key function and reduce each group with a binary operation.

        Example:
            >>> IterChain([1, 2, 3, 4]).into_reduced_groups(
            ...     lambda x: x % 2, sum
            ... ).unwrap()  # {1: 4, 0: 6}
        """
        return DictChain(_value=cz.itertoolz.reduceby(key, binop, self.unwrap()))

    def into_frequencies(self) -> "DictChain[V, int]":
        """
        Count the frequency of each element in the iterable.

        Example:
            >>> IterChain(
            ...     [1, 2, 2, 3]
            ... ).into_frequencies().unwrap()  # {1: 1, 2: 2, 3: 1}
        """
        return DictChain(_value=cz.itertoolz.frequencies(self.unwrap()))


@dataclass(slots=True, frozen=True, repr=False)
class DictChain[K, V](BaseDictChain[K, V]):
    """
    DictChain enables chaining, transformation, and aggregation of dictionaries.

    Example:
        >>> DictChain({"a": 1, "b": 2}).map_values(
        ...     lambda v: v * 10
        ... ).unwrap()  # {'a': 10, 'b': 20}
        >>> DictChain({"a": 1, "b": 2}).agg_values(sum).unwrap()  # 3
    """

    @property
    def get_key(self) -> Getter[K]:
        """
        Return a Getter for the dictionary's keys.

        Example:
            >>> DictChain({"a": 1}).get_key.first().unwrap()  # 'a'
        """
        return Getter(_value=self.unwrap().keys())

    @property
    def get_value(self) -> Getter[V]:
        """
        Return a Getter for the dictionary's values.

        Example:
            >>> DictChain({"a": 1}).get_value.first().unwrap()  # 1
        """
        return Getter(_value=self.unwrap().values())

    @property
    def get_item(self) -> Getter[tuple[K, V]]:
        """
        Return a Getter for the dictionary's items.

        Example:
            >>> DictChain({"a": 1}).get_item.first().unwrap()  # ('a', 1)
        """
        return Getter(_value=self.unwrap().items())

    def agg_keys[K1](self, on: AggFunc[K, K1]) -> ScalarChain[K1]:
        """
        Aggregate the dictionary's keys using the provided aggregation function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_keys(list).unwrap()  # ['a', 'b']
        """
        return ScalarChain(_value=on(self.unwrap().keys()))

    def agg_values[V1](self, on: AggFunc[V, V1]) -> ScalarChain[V1]:
        """
        Aggregate the dictionary's values using the provided aggregation function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_values(sum).unwrap()  # 3
        """
        return ScalarChain(_value=on(self.unwrap().values()))

    def agg_items[V1](self, on: AggFunc[tuple[K, V], V1]) -> ScalarChain[V1]:
        """
        Aggregate the dictionary's items using the provided aggregation function.

        Example:
            >>> DictChain({"a": 1, "b": 2}).agg_items(len).unwrap()  # 2
        """
        return ScalarChain(_value=on(self.unwrap().items()))

    def into_iter_keys(self) -> "IterChain[K]":
        """
        Convert the dictionary's keys into an IterChain.

        Example:
            >>> DictChain(
            ...     {"a": 1, "b": 2}
            ... ).into_iter_keys().convert_to.list()  # ['a', 'b']
        """
        return IterChain(_value=self.unwrap().keys())

    def into_iter_values(self) -> IterChain[V]:
        """
        Convert the dictionary's values into an IterChain.

        Example:
            >>> DictChain(
            ...     {"a": 1, "b": 2}
            ... ).into_iter_values().convert_to.list()  # [1, 2]
        """
        return IterChain(_value=self.unwrap().values())

    def into_iter_items(self) -> IterChain[tuple[K, V]]:
        """
        Convert the dictionary's items into an IterChain.

        Example:
            >>> DictChain(
            ...     {"a": 1, "b": 2}
            ... ).into_iter_items().convert_to.list()  # [('a', 1), ('b', 2)]
        """
        return IterChain(_value=self.unwrap().items())
