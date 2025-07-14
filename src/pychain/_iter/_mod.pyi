from collections.abc import Callable, Iterable
from random import Random
from typing import Any, Self

import polars as pl
from numpy.typing import NDArray

from .._protocols import CheckFunc, ProcessFunc, TransformFunc

class Iter[V]:
    """
    Fournit un itérateur chaînable pour les transformations de données paresseuses.

    `Iter` est un conteneur pour les séquences de données qui permet d'enchaîner
    des opérations de manière déclarative. Il est conçu pour être paresseux, ce qui
    signifie que les transformations ne sont pas exécutées tant qu'une méthode
    terminale (par exemple, `.to_list()`, `.unwrap()`) n'est pas appelée.

    Cela permet de construire des pipelines de traitement de données complexes et
    efficaces en mémoire, car les données ne sont itérées qu'une seule fois,
    à la toute fin.

    Attributes:
        V: Le type des éléments dans l'itérateur.

    Examples:
        Créer un `Iter` et enchaîner plusieurs opérations.
        >>> import pychain as pc
        >>> data = range(10)
        >>> result = (
        ...     pc.Iter(data)
        ...     .filter(pc.op().gt(2))  # [3, 4, 5, 6, 7, 8, 9]
        ...     .map(pc.op().mul(10))  # [30, 40, 50, 60, 70, 80, 90]
        ...     .head(3)  # [30, 40, 50]
        ...     .to_list()
        ... )
        >>> result
        [30, 40, 50]

        Utiliser des expressions pour des transformations complexes.
        >>> import pychain as pc
        >>> square_and_add_one = pc.op().pow(2).add(1)
        >>> pc.Iter([1, 2, 3]).map(square_and_add_one).to_list()
        [2, 5, 10]
    """

    _value: Iterable[V]
    _pipeline: list[Callable[[Iterable[V]], Any]]

    def __init__(
        self,
        _value: Iterable[V],
        _pipeline: list[Callable[[Iterable[V]], Any]] | None = None,
    ) -> None: ...
    def clone(self) -> Self: ...
    def unwrap(self) -> Iterable[V]: ...
    def group_by[K](self, on: TransformFunc[V, K]) -> dict[K, list[V]]: ...
    def into_frequencies(self) -> dict[V, int]: ...
    def reduce_by[K](
        self, key: TransformFunc[V, K], binop: Callable[[V, V], V]
    ) -> "Iter[K]": ...
    def agg[V1](self, on: Callable[[Iterable[V]], V1]) -> V1: ...
    def map[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Applique une fonction sur chaque élément.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).map(pc.op().mul(2)).to_list()
            [2, 4]
        """
        ...

    def flat_map[V1](self, f: TransformFunc[V, Iterable[V1]]) -> "Iter[V1]":
        """
        Applique une fonction et aplatit le résultat.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).flat_map(lambda x: [x, x * 10]).to_list()
            [1, 10, 2, 20]
        """
        ...

    def starmap[V1](self, f: TransformFunc[V, V1]) -> "Iter[V1]":
        """
        Applique une fonction sur chaque élément, en décompressant les arguments.

        Example:
            >>> import pychain as pc
            >>> from operator import add
            >>> data = [(1, 2), (3, 4)]
            >>> pc.Iter(data).starmap(add).to_list()
            [3, 7]
        """
        ...

    def compose[V1](self, *fns: TransformFunc[V, V1]) -> "Iter[V1]": ...
    def take_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Prend les éléments tant qu'un prédicat est vrai.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 2]).take_while(pc.op().lt(3)).to_list()
            [1, 2]
        """
        ...

    def drop_while(self, predicate: CheckFunc[V]) -> Self:
        """
        Ignore les éléments tant qu'un prédicat est vrai.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 2]).drop_while(pc.op().lt(3)).to_list()
            [3, 2]
        """
        ...

    def interleave(self, *others: Iterable[V]) -> Self:
        """
        Entrelace l'itérable avec d'autres.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).interleave([10, 20]).to_list()
            [1, 10, 2, 20]
        """
        ...

    def interpose(self, element: V) -> Self:
        """
        Insère un élément entre chaque paire d'éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).interpose(0).to_list()
            [1, 0, 2, 0, 3]
        """
        ...

    def top_n(self, n: int, key: Callable[[V], Any] | None = None) -> Self:
        """
        Retourne les N plus grands éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 5, 3, 2]).top_n(2).to_list()
            [5, 3]
        """
        ...

    def random_sample(
        self, probability: float, state: Random | int | None = None
    ) -> Self:
        """
        Échantillonne aléatoirement des éléments avec une probabilité donnée.

        Example:
            >>> import pychain as pc
            >>> pc.Iter(range(100)).random_sample(probability=0.01, state=1).to_list()
            [13, 91]
        """
        ...

    def concat(self, *others: Iterable[V]) -> Self:
        """
        Concatène l'itérable avec d'autres.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).concat([3, 4]).to_list()
            [1, 2, 3, 4]
        """
        ...

    def filter(self, f: CheckFunc[V]) -> Self:
        """
        Filtre les éléments selon un prédicat.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).filter(pc.op().gt(1)).to_list()
            [2, 3]
        """
        ...

    def accumulate(self, f: Callable[[V, V], V]) -> Self:
        """
        Accumule les valeurs en utilisant une fonction binaire.

        Example:
            >>> import pychain as pc
            >>> from operator import add
            >>> pc.Iter([1, 2, 3]).accumulate(add).to_list()
            [1, 3, 6]
        """
        ...

    def insert_left(self, value: V) -> Self:
        """
        Ajoute une valeur au début.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([2, 3]).insert_left(1).to_list()
            [1, 2, 3]
        """
        ...

    def peek(self, note: str | None = None) -> Self:
        """
        Inspecte les éléments, en les affichant avec une note optionnelle.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).peek("step 1").to_list()
            Peeked value (step 1): 1
            [1, 2, 3]
        """
        ...

    def peekn(self, n: int, note: str | None = None) -> Self:
        """
        Inspecte les N premiers éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4, 5, 6]).peekn(3, "step 1").to_list()
            Peeked 3 values (step 1): [1, 2, 3]
            [1, 2, 3, 4, 5, 6]
        """
        ...

    def head(self, n: int) -> Self:
        """
        Prend les N premiers éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4]).head(2).to_list()
            [1, 2]
        """
        ...

    def tail(self, n: int) -> Self:
        """
        Prend les N derniers éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4]).tail(2).to_list()
            [3, 4]
        """
        ...

    def drop_first(self, n: int) -> Self:
        """
        Ignore les N premiers éléments.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4]).drop_first(2).to_list()
            [3, 4]
        """
        ...

    def every(self, index: int) -> Self:
        """
        Prend un élément à chaque N-ième position.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([0, 1, 2, 3, 4]).every(2).to_list()
            [0, 2, 4]
        """
        ...

    def repeat(self, n: int) -> Self:
        """
        Répète chaque élément N fois.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).repeat(2).to_list()
            [1, 1, 2, 2]
        """
        ...

    def unique(self) -> Self:
        """
        Retourne les éléments uniques, en préservant l'ordre.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 2, 3]).unique().to_list()
            [1, 2, 3]
        """
        ...

    def cumsum(self) -> Self:
        """
        Calcule la somme cumulative.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).cumsum().to_list()
            [1, 3, 6]
        """
        ...

    def cumprod(self) -> Self:
        """
        Calcule le produit cumulatif.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).cumprod().to_list()
            [1, 2, 6]
        """
        ...

    def merge_sorted(
        self, *others: Iterable[V], sort_on: Callable[[V], Any] | None = None
    ) -> Self:
        """
        Fusionne et trie avec d'autres itérables.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 3]).merge_sorted([2, 4]).to_list()
            [1, 2, 3, 4]
        """
        ...

    def tap(self, func: Callable[[V], None]) -> Self:
        """
        Applique une fonction avec effet de bord sur chaque élément.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).tap(print).to_list()
            1
            2
            [1, 2]
        """
        ...

    def zip_with(
        self, *others: Iterable[V], strict: bool = False
    ) -> "Iter[tuple[V, ...]]":
        """
        Combine les éléments avec d'autres itérables.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2]).zip_with([10, 20]).to_list()
            [(1, 10), (2, 20)]
        """
        ...

    def enumerate(self) -> "Iter[tuple[int, V]]":
        """
        Énumère l'itérable.

        Example:
            >>> import pychain as pc
            >>> pc.Iter(["a", "b"]).enumerate().to_list()
            [(0, 'a'), (1, 'b')]
        """
        ...

    def flatten(self) -> "Iter[Any]":
        """
        Aplatit les itérables imbriqués.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([[1, 2], [3, 4]]).flatten().to_list()
            [1, 2, 3, 4]
        """
        ...

    def diff(
        self,
        *others: Iterable[V],
        default: Any | None = None,
        key: ProcessFunc[V] | None = None,
    ) -> "Iter[tuple[V, ...]]":
        """
        Calcule la différence entre les itérables.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).diff([1, 2, 10, 100]).to_list()
            [(3, 10), (None, 100)]
            >>> pc.Iter([1, 2, 3]).diff([1, 2, 10, 100], default="foo").to_list()
            [(3, 10), ('foo', 100)]
            >>> pc.Iter(["apples", "bananas"]).diff(
            ...     ["Apples", "Oranges"], key=str.lower
            ... ).to_list()
            [('bananas', 'Oranges')]
        """
        ...

    def partition(self, n: int, pad: V | None = None) -> "Iter[tuple[V, ...]]":
        """
        Partitionne en morceaux de taille N, avec remplissage optionnel.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4, 5]).partition(2, pad=0).to_list()
            [(1, 2), (3, 4), (5, 0)]
        """
        ...

    def partition_all(self, n: int) -> "Iter[tuple[V, ...]]":
        """
        Partitionne en morceaux de taille N, le dernier pouvant être plus petit.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4, 5]).partition_all(2).to_list()
            [(1, 2), (3, 4), (5,)]
        """
        ...

    def rolling(self, length: int) -> "Iter[tuple[V, ...]]":
        """
        Crée une fenêtre glissante de longueur donnée.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3, 4]).rolling(3).to_list()
            [(1, 2, 3), (2, 3, 4)]
        """
        ...

    def cross_join[V1](self, other: Iterable[V1]) -> "Iter[tuple[V1, V]]":
        """
        Crée un `Iter` à partir du produit cartésien des itérables.

        Example:
            >>> import pychain as pc
            >>> pc.Iter(range(0, 2)).cross_join(["a", "b"]).to_list()
            [('a', 0), ('a', 1), ('b', 0), ('b', 1)]
        """
        ...

    def first(self) -> V:
        """
        Retourne le premier élément.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([10, 20, 30]).first()
            10
        """
        ...

    def second(self) -> V:
        """
        Retourne le deuxième élément.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([10, 20, 30]).second()
            20
        """
        ...

    def last(self) -> V:
        """
        Retourne le dernier élément.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([10, 20, 30]).last()
            30
        """
        ...

    def at_index(self, index: int) -> V:
        """
        Retourne l'élément à l'index spécifié.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([10, 20, 30]).at_index(2)
            30
        """
        ...

    def len(self) -> int:
        """
        Calcule et retourne la longueur de l'itérable.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([10, 20, 30]).len()
            3
        """
        ...

    def to_obj[T](self, obj: Callable[[Iterable[V]], T]) -> T:
        """
        Convertit l'itérable en un objet personnalisé via une fonction.

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 3]).to_obj(tuple)
            (1, 2, 3)
        """
        ...

    def to_list(self) -> list[V]:
        """
        Convertit l'itérable en liste.

        Example:
            >>> import pychain as pc
            >>> pc.Iter(range(3)).to_list()
            [0, 1, 2]
        """
        ...

    def to_set(self) -> set[V]:
        """
        Convertit l'itérable en ensemble (set).

        Example:
            >>> import pychain as pc
            >>> pc.Iter([1, 2, 1]).to_set()
            {1, 2}
        """
        ...

    def to_dict(self) -> dict[int, V]:
        """
        Convertit l'itérable en dictionnaire avec les indices comme clés.

        Example:
            >>> import pychain as pc
            >>> pc.Iter(["a", "b"]).to_dict()
            {0: 'a', 1: 'b'}
        """
        ...

    def to_array(self) -> NDArray[Any]:
        """
        Convertit l'itérable en tableau NumPy.

        Example:
            >>> import pychain as pc
            >>> arr = pc.Iter([1, 2, 3]).to_array()
            >>> arr.shape
            (3,)
        """
        ...

    def to_series(self) -> pl.Series:
        """
        Convertit l'itérable en Series Polars.

        Example:
            >>> import pychain as pc
            >>> s = pc.Iter([1, 2, 3]).to_series()
            >>> s.name
            ''
        """
        ...
