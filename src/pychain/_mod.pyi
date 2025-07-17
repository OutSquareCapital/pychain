"""stubs for pychain - Chainable expressions for functional-style data processing."""

from collections.abc import Callable, Container, Iterable
from random import Random
from typing import Any, Self

from ._protocols import CheckFunc, ProcessFunc, TransformFunc

op: OpConstructor
"""
Constructs chainable operations for functional-style data processing.
"""
it: IterConstructor
"""Constructs chainable iterators-focused functions for functional-style data processing.
"""
struct: StructConstructor
"""Constructs chainable dict-focused functions for functional-style data processing."""


class StructConstructor:
    def __call__[K, V](self, ktype: type[K], vtype: type[V]) -> Struct[K, V, K, V]: ...

class IterConstructor:
    def __call__[T](self, *dtype: type[T]) -> Iter[T, T]: ...

class OpConstructor:
    """
    Constructs chainable operations for functional-style data processing.

    Main entry point for creating operations in pychain.

    This class is not meant to be instantiated directly, but rather through the `pc.op()` constructor.
    """
    def __call__[T](self, *dtype: type[T]) -> Op[T, T]:
        """
        Create a chainable operation.

        The `dtype` argument is used to specify the type of the input of the operation.

        The output will be refined at each step of the chain.

        This allows you to build a pipeline, and get back an Op that is inferred, just like a function.

        The type in itself is ignored at runtime.

        You can pass any type: an `int`, a `str`, etc.

        If the type is Iterable (a polars `Series`, a list, a tuple, etc.), you probably want to use the `iter` constructor instead.

        Example:
            >>> import pychain as pc
            >>> pc.op(int).add(5).into(str)(10)
            '15'
        """
        ...

class Op[P, R]:
    """
    Read like `Callable[[P], R]`, or `def foo(p: P) -> R`.

    Crée une opération chainable pour des transformations de données de style fonctionnel.

    `Op` est le cœur du constructeur d'expressions de pychain.

    Il est conçu pour ne pas être instancié directement, mais via le constructeur `pc.op()`.

    Il permet de construire des pipelines de transformations complexes qui sont
    évaluées de manière paresseuse.

    Chaque méthode appelée sur une instance de `pc.op()` compose la nouvelle fonction avec l'ancienne.
    L'opération finale est un callable qui peut être exécuté en lui passant une valeur.

    Example:
        >>> import pychain as pc
        >>> add_5_and_double = pc.op().add(5).mul(2)
        >>> add_5_and_double(10)
        30
    """

    def __call__(self, value: P) -> R:
        """
        Exécute le pipeline avec la valeur d'entrée fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().add(1)(5)
            6
        """
        ...

    def into[T](self, obj: Callable[[R], T]) -> "Op[P, T]":
        """
        Transforme la sortie du pipeline à l'aide du callable fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().add(1).into(str)(5)
            '6'
        """
        ...

    def hint[T](self, dtype: type[T]) -> "Op[P, T]":
        """
        Fournit une indication de type pour la sortie de l'opération (n'affecte pas l'exécution).

        Example:
            >>> import pychain as pc
            >>> operation = pc.op().hint(int)
            >>> operation("42")  # Note: hint ne convertit pas la valeur.
            '42'
        """
        ...
    def add(self, value: R) -> Self:
        """
        Ajoute une valeur à la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().add(5)(10)
            15
        """
        ...

    def sub(self, value: R) -> Self:
        """
        Soustrait une valeur de la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().sub(5)(10)
            5
        """
        ...

    def mul(self, value: R) -> Self:
        """
        Multiplie la sortie du pipeline par une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().mul(5)(10)
            50
        """
        ...

    def truediv(self, value: R) -> "Op[P, float]":
        """
        Divise la sortie du pipeline par une valeur (division réelle).

        Example:
            >>> import pychain as pc
            >>> pc.op().truediv(2)(10)
            5.0
        """
        ...

    def floordiv(self, value: R) -> "Op[P, float]":
        """
        Divise la sortie du pipeline par une valeur (division entière).

        Example:
            >>> import pychain as pc
            >>> pc.op().floordiv(3)(10)
            3
        """
        ...

    def sub_r(self, value: R) -> Self:
        """
        Soustrait la sortie du pipeline d'une valeur (soustraction inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().sub_r(10)(5)
            5
        """
        ...

    def truediv_r(self, value: R) -> Self:
        """
        Divise une valeur par la sortie du pipeline (division réelle inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().truediv_r(10)(2)
            5.0
        """
        ...

    def floordiv_r(self, value: R) -> Self:
        """
        Divise une valeur par la sortie du pipeline (division entière inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().floordiv_r(10)(3)
            3
        """
        ...

    def mod(self, value: R) -> Self:
        """
        Calcule le modulo de la sortie du pipeline par une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().mod(3)(10)
            1
        """
        ...

    def pow(self, value: R) -> Self:
        """
        Élève la sortie du pipeline à la puissance d'une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().pow(2)(3)
            9
        """
        ...

    def neg(self) -> Self:
        """
        Applique la négation à la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().neg()(5)
            -5
        """
        ...

    def round_to(self, ndigits: int) -> "Op[P, float]":
        """
        Arrondit la sortie du pipeline au nombre de décimales spécifié.

        Example:
            >>> import pychain as pc
            >>> pc.op().round_to(2)(3.14159)
            3.14
        """
        ...

    def and_(self, *others: Callable[[P], bool]) -> "Op[P, bool]":
        """
        Chains multiple boolean operations using a logical AND.

        This method takes one or more other callable operations and ...
        Op.

        When this new operation is called with a value, it will
        ...
        operations ...

        Example:
            >>> import pychain as pc
            >>> pc.op(int).gt(5).and_(pc.op().lt(10), pc.op().gt(2))(7)
            True
        """
        ...
    def is_true(self) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est "truthy".

        Example:
            >>> import pychain as pc
            >>> pc.op().is_true()(1)
            True
        """
        ...

    def is_none(self) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est None.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_none()(None)
            True
        """
        ...

    def is_not_none(self) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline n'est pas None.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_not_none()(5)
            True
        """
        ...

    def is_in(self, values: Container[R]) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est dans le conteneur fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_in([1, 2, 3])(2)
            True
        """
        ...

    def is_not_in(self, values: Container[R]) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline n'est pas dans le conteneur fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_not_in([1, 2, 3])(4)
            True
        """
        ...

    def is_iterable(self) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est un itérable.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_iterable()([1, 2, 3])
            True
        """
        ...

    def eq(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().eq(5)(5)
            True
        """
        ...

    def ne(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est différente de la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().ne(5)(3)
            True
        """
        ...

    def gt(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est strictement supérieure à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().gt(3)(5)
            True
        """
        ...

    def ge(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est supérieure ou égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().ge(5)(5)
            True
        """
        ...

    def lt(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est strictement inférieure à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().lt(5)(3)
            True
        """
        ...

    def le(self, value: R) -> "Op[P, bool]":
        """
        Vérifie si la sortie du pipeline est inférieure ou égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().le(5)(5)
            True
        """
        ...

class Iter[V, V1]:
    """Iter[V, V1] is a chainable iterator that allows functional-style data processing.
    Unlike `Op`, the chain itself is not callable. You have to call the `iter` method to instanciate a Contain[V, V1] object.
    This design choice ensure that you materialize the iterator in something concrete, because here the lazy is layered: the methods themselves, and the underlying object!.
    """
    def into[T](self, obj: Callable[[Iterable[V]], T]) -> Contain[V, T]: ...
    def group_by[K](self, on: TransformFunc[V, K]) -> dict[K, list[V]]: ...
    def into_frequencies(self) -> dict[V, int]: ...
    def reduce_by[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "Iter[V, K]": ...
    def map[T](self, f: TransformFunc[V, T]) -> "Iter[V, T]": ...
    def flat_map(self, f: TransformFunc[V, Iterable[V1]]) -> Self: ...
    def starmap(self, f: TransformFunc[V, V1]) -> Self: ...
    def compose(self, *fns: TransformFunc[V, V1]) -> Self: ...
    def take_while(self, predicate: CheckFunc[V]) -> Self: ...
    def drop_while(self, predicate: CheckFunc[V]) -> Self: ...
    def interleave(self, *others: Iterable[V]) -> Self: ...
    def interpose(self, element: V) -> Self: ...
    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self: ...
    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self: ...
    def concat(self, *others: Iterable[V]) -> Self: ...
    def filter(self, f: CheckFunc[V]) -> Self: ...
    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Repeatedly apply binary function to a sequence, accumulating results.

        Example:
            >>> import pychain as pc
            >>> pc.it(int).accumulate(lambda x, y: x + y).into(list)([1, 2, 3, 4, 5])
            [1, 3, 6, 10, 15]
        """
        ...
    def insert_left(self, value: V) -> Self: ...
    def peek(self, note: str | None = None) -> Self: ...
    def peekn(self, n: int, note: str | None = None) -> Self: ...
    def head(self, n: int) -> Self: ...
    def tail(self, n: int) -> Self: ...
    def drop_first(self, n: int) -> Self: ...
    def every(self, index: int) -> Self: ...
    def repeat(self, n: int) -> Self: ...
    def unique(self) -> Self: ...
    def cumsum(self) -> Self: ...
    def cumprod(self) -> Self: ...
    def merge_sorted(
        self, others: Iterable[Iterable[V]], sort_on: Callable[[V], Any] | None = None
    ) -> Self: ...
    def tap(self, func: Callable[[V], None]) -> Self: ...
    def zip_with(
        self, others: Iterable[Iterable[V]], strict: bool = False
    ) -> "Iter[V, tuple[V, ...]]": ...
    def enumerate(self) -> "Iter[V, tuple[int, V]]": ...
    def flatten(self) -> "Iter[V, Any]": ...
    def diff(
        self,
        others: Iterable[Iterable[V]],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ) -> "Iter[V, tuple[V, ...]]": ...
    def partition(self, n: int, pad: V | None = None) -> "Iter[V, tuple[V, ...]]": ...
    def partition_all(self, n: int) -> "Iter[V, tuple[V, ...]]": ...
    def rolling(self, length: int) -> "Iter[V, tuple[V, ...]]": ...
    def cross_join(self, other: Iterable[V1]) -> "Iter[V, tuple[V1, V]]": ...
    def first(self) -> Op[Iterable[V], V1]: ...
    def second(self) -> Op[Iterable[V], V1]: ...
    def last(self) -> Op[Iterable[V], V1]: ...
    def length(self) -> Op[Iterable[V], int]: ...
    def mean(self) -> Op[Iterable[V], float]: ...
    def median(self) -> Op[Iterable[V], float]: ...
    def mode(self) -> Op[Iterable[V], V1]: ...
    def stdev(self) -> Op[Iterable[V], float]: ...
    def variance(self) -> Op[Iterable[V], float]: ...
    def pvariance(self) -> Op[Iterable[V], float]: ...
    def median_low(self) -> Op[Iterable[V], float]: ...
    def median_high(self) -> Op[Iterable[V], float]: ...
    def median_grouped(self) -> Op[Iterable[V], float]: ...
    def sum(self) -> Op[Iterable[V], float]: ...
    def min(self) -> Op[Iterable[V], float]: ...
    def max(self) -> Op[Iterable[V], float]: ...

class Contain[V, V1]:
    """This is the executor for the Iter chain.
    The method "into_iter" allows you to go back in an iter Chain.
    """
    def __call__(self, value: Iterable[V]) -> V1: ...
    def into_iter(self) -> Iter[V, V1]: ...

class Struct[K, V, K1, V1]:
    def __call__(self, value: dict[K, V]) -> dict[K1, V1]: ...
    def map_keys[T](self, f: TransformFunc[K, T]) -> "Struct[K, V, T, V1]": ...
    def map_values[T](self, f: TransformFunc[V, T]) -> "Struct[K, V1, K1, T]": ...
    def select(self, predicate: CheckFunc[K]) -> Self: ...
    def filter(self, predicate: CheckFunc[V]) -> Self: ...
    def filter_on_key(self, key: K, predicate: CheckFunc[V]) -> Self: ...
    def with_key(self, key: K, value: V) -> Self: ...
    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self: ...
    def update_in(self, *keys: K, f: ProcessFunc[V]) -> Self: ...
    def merge(self, *others: dict[K, V]) -> Self: ...
    def merge_with(
        self, f: Callable[[Iterable[V]], V], *others: dict[K, V]
    ) -> Self: ...
    def drop(self, *keys: K) -> Self: ...
    def flatten_keys(self) -> "Struct[K, V, str, V1]": ...
    def to_obj[T](self, obj: Callable[[dict[K, V]], T]) -> T: ...
