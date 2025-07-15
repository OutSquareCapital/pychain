from collections.abc import Callable, Iterable
from typing import Self

import polars as pl

from .._protocols import CheckFunc, ProcessFunc, TransformFunc

class Struct[K, V]:
    """
    Fournit une structure de données immuable, semblable à un dictionnaire, pour des transformations chaînables.

    `Struct` est conçu pour des opérations sur des données structurées (clé-valeur),
    en offrant une API déclarative et paresseuse. Les transformations sont
    enchaînées et ne sont exécutées que lorsqu'une méthode terminale comme `.unwrap()`
    est appelée.

    Cela favorise un code plus lisible et prévisible en encourageant l'utilisation
    d'expressions pures via `pc.op()` plutôt que des lambdas.

    Attributes:
        K: Le type des clés dans la structure.
        V: Le type des valeurs dans la structure.

    Examples:
        Créer un `Struct` et enchaîner plusieurs opérations de transformation.
        >>> import pychain as pc
        >>> data = {"a": 1, "b": 2, "c": 3}
        >>> result = (
        ...     pc.Struct(data)
        ...     .map_values(pc.op().add(10))  # {'a': 11, 'b': 12, 'c': 13}
        ...     .select(pc.op().is_in(["a", "c"]))  # {'a': 11, 'c': 13}
        ...     .unwrap()
        ... )
        >>> result
        {'a': 11, 'c': 13}
    """

    _value: dict[K, V]
    _pipeline: list[Callable[[dict[K, V]], dict[K, V]]]

    def __init__(
        self,
        _value: dict[K, V],
        _pipeline: list[Callable[[dict[K, V]], dict[K, V]]] | None = None,
    ) -> None: ...
    def clone(self) -> Self:
        """
        Crée une copie indépendante du `Struct` et de son pipeline.

        Example:
            >>> import pychain as pc
            >>> a = pc.Struct({"x": 1})
            >>> b = a.clone().with_key("y", 2)
            >>> a.unwrap()
            {'x': 1}
            >>> b.unwrap()
            {'x': 1, 'y': 2}
        """
        ...

    def unwrap(self) -> dict[K, V]:
        """
        Exécute le pipeline de transformations et retourne le dictionnaire final.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1}).map_values(pc.op().add(1)).unwrap()
            {'a': 2}
        """
        ...

    def _into[K1, V1](
        self, f: Callable[[dict[K, V]], dict[K1, V1]]
    ) -> "Struct[K1, V1]": ...
    def map_keys[K1](self, f: TransformFunc[K, K1]) -> "Struct[K1, V]":
        """
        Applique une fonction sur les clés.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1}).map_keys(str.upper).unwrap()
            {'A': 1}
        """
        ...

    def map_values[V1](self, f: TransformFunc[V, V1]) -> "Struct[K, V1]":
        """
        Applique une fonction sur les valeurs.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1}).map_values(pc.op().add(10)).unwrap()
            {'a': 11}
        """
        ...

    def select(self, predicate: CheckFunc[K]) -> Self:
        """
        Sélectionne les paires clé-valeur en fonction d'un prédicat sur les clés.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1, "b": 2}).select(pc.op().eq("a")).unwrap()
            {'a': 1}
        """
        ...

    def filter(self, predicate: CheckFunc[V]) -> Self:
        """
        Filtre les paires clé-valeur en fonction d'un prédicat sur les valeurs.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1, "b": 2}).filter(pc.op().gt(1)).unwrap()
            {'b': 2}
        """
        ...

    def filter_on_key(self, key: K, predicate: CheckFunc[V]) -> Self:
        """
        Applique un prédicat à la valeur de la clé spécifiée, en supprimant
        l'élément si le prédicat est faux. Les autres éléments sont conservés.

        Example:
            >>> import pychain as pc
            >>> data = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
            >>> pc.Struct(data).filter_on_key("b", pc.op.item(0, int).ne(1)).unwrap()
            {'a': [1, 2], 'b': [3, 4], 'c': [5, 6]}
        """
        ...

    def with_key(self, key: K, value: V) -> Self:
        """
        Ajoute ou met à jour une paire clé-valeur.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1}).with_key("b", 2).unwrap()
            {'a': 1, 'b': 2}
        """
        ...

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        """
        Ajoute ou met à jour une valeur dans un chemin imbriqué.

        Example:
            >>> import pychain as pc
            >>> data = {"a": {"b": 1}}
            >>> pc.Struct(data).with_nested_key(["a", "c"], 2).unwrap()
            {'a': {'b': 1, 'c': 2}}
        """
        ...

    def update_in(self, *keys: K, f: ProcessFunc[V]) -> Self:
        """
        Met à jour une valeur dans un chemin imbriqué à l'aide d'une fonction.

        Example:
            >>> import pychain as pc
            >>> data = {"a": {"b": 1}}
            >>> pc.Struct(data).update_in("a", "b", f=pc.op().add(10)).unwrap()
            {'a': {'b': 11}}
        """
        ...

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Fusionne avec d'autres dictionnaires.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1}).merge({"b": 2}, {"c": 3}).unwrap()
            {'a': 1, 'b': 2, 'c': 3}
        """
        ...

    def merge_with(self, f: Callable[[Iterable[V]], V], *others: dict[K, V]) -> Self:
        """
        Fusionne avec d'autres dictionnaires, en combinant les valeurs avec une fonction.

        Example:
            >>> import pychain as pc
            >>> d1 = {"a": 1, "b": 2}
            >>> d2 = {"a": 10, "c": 3}
            >>> pc.Struct(d1).merge_with(sum, d2).unwrap()
            {'a': 11, 'c': 3, 'b': 2}
        """
        ...

    def drop(self, *keys: K) -> Self:
        """
        Supprime des clés du dictionnaire.

        Example:
            >>> import pychain as pc
            >>> pc.Struct({"a": 1, "b": 2, "c": 3}).drop("a", "c").unwrap()
            {'b': 2}
        """
        ...

    def flatten_keys(self) -> "Struct[str, V]":
        """
        Aplatit les clés imbriquées en une seule chaîne de caractères.

        Example:
            >>> import pychain as pc
            >>> data = {"a": {"b": 1, "c": 2}}
            >>> pc.Struct(data).flatten_keys().unwrap()
            {'a.b': 1, 'a.c': 2}
        """
        ...

    def to_obj[T](self, obj: Callable[[dict[K, V]], T]) -> T:
        """
        Convertit le `Struct` en un objet personnalisé via une fonction.

        Example:
            >>> import pychain as pc
            >>> from collections import namedtuple
            >>> Point = namedtuple("Point", ["x", "y"])
            >>> pc.Struct({"x": 1, "y": 2}).to_obj(lambda d: Point(**d))
            Point(x=1, y=2)
        """
        ...

    def to_frame(self) -> pl.DataFrame:
        """
        Convertit le `Struct` en DataFrame Polars.

        Example:
            >>> import pychain as pc
            >>> data = {"col1": [1, 2], "col2": [3, 4]}
            >>> df = pc.Struct(data).to_frame()
            >>> df.shape
            (2, 2)
        """
        ...
