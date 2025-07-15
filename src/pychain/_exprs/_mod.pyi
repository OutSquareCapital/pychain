from collections.abc import Callable, Container
from typing import Any, overload

class OpConstructor:
    """
    Constructs chainable operations for functional-style data processing.

    Main entry point for creating operations in pychain.

    This class is not meant to be instantiated directly, but rather through the `pc.op()` constructor.
    """
    @overload
    def __call__(self) -> ChainableOp[Any, Any]:
        """
        Create a new chainable operation without any initial type hint.

        """
        ...
    @overload
    def __call__[T](self, *dtype: type[T]) -> ChainableOp[T, Any]:
        """
        Infer the type of the operation based on the provided type hint.

        This is the recommended way to use the constructor, as this allows you to truly define the chain as if you were typing a function signature.

        This does not change the runtime behavior, but provides type hints, so you know which type go in -> go out.
        You can pass any type: a polars Series, an int, a str, etc.

        Example:
            >>> import pychain as pc
            >>> pc.op(int).add(5).into(str)(10)
            '15'
        """
        ...

    def attr[T](self, name: str, dtype: type[T]) -> "ChainableOp[T, Any]":
        """
        Accède à un attribut de la sortie du pipeline.

        Must specifiy type hints to ensure type safety.

        Example:
            >>> import pychain as pc
            >>> class MyObject:
            ...     def __init__(self, value):
            ...         self.value = value
            >>> pc.op.attr("value", int)(MyObject(42))
            42
        """
        ...

    def item[T](self, key: Any, dtype: type[T]) -> "ChainableOp[T, Any]":
        """
        Accède à un élément de la sortie du pipeline.

        Must specify type hints to ensure type safety.

        Example:
            >>> import pychain as pc
            >>> get_key = pc.op.item("key", str)
            >>> get_key({"key": "value"})
            'value'
        """
        ...

class ChainableOp[P, R]:
    """
    Crée une opération chainable pour des transformations de données de style fonctionnel.

    `ChainableOp` est le cœur du constructeur d'expressions de pychain. Il est conçu
    pour ne pas être instancié directement, mais via le constructeur `pc.op()`.

    Il permet de construire des pipelines de transformations complexes qui sont
    évaluées de manière paresseuse.

    Chaque méthode appelée sur une instance de `pc.op()` compose la nouvelle fonction avec l'ancienne.
    L'opération finale est un callable qui peut être exécuté en lui passant une valeur.

    Attributes:
        P: Le type du paramètre d'entrée de l'opération.
        R: Le type du résultat de l'opération.

    Examples:
        Créer et utiliser une opération simple.
        >>> import pychain as pc
        >>> add_5_and_double = pc.op().add(5).mul(2)
        >>> add_5_and_double(10)
        30

        Utiliser une opération dans une chaîne `Iter`.
        >>> data = pc.Iter(range(5))
        >>> expr = pc.op().pow(2)
        >>> data.map(expr).to_list()
        [0, 1, 4, 9, 16]
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

    def into[T](self, obj: Callable[[R], T]) -> "ChainableOp[P, T]":
        """
        Transforme la sortie du pipeline à l'aide du callable fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().add(1).into(str)(5)
            '6'
        """
        ...

    def hint[T](self, dtype: type[T]) -> "ChainableOp[P, T]":
        """
        Fournit une indication de type pour la sortie de l'opération (n'affecte pas l'exécution).

        Example:
            >>> import pychain as pc
            >>> operation = pc.op().hint(int)
            >>> operation("42")  # Note: hint ne convertit pas la valeur.
            '42'
        """
        ...

    def add(self, value: R) -> "ChainableOp[P, R]":
        """
        Ajoute une valeur à la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().add(5)(10)
            15
        """
        ...

    def sub(self, value: R) -> "ChainableOp[P, R]":
        """
        Soustrait une valeur de la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().sub(5)(10)
            5
        """
        ...

    def mul(self, value: R) -> "ChainableOp[P, R]":
        """
        Multiplie la sortie du pipeline par une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().mul(5)(10)
            50
        """
        ...

    def truediv(self, value: R) -> "ChainableOp[P, float]":
        """
        Divise la sortie du pipeline par une valeur (division réelle).

        Example:
            >>> import pychain as pc
            >>> pc.op().truediv(2)(10)
            5.0
        """
        ...

    def floordiv(self, value: R) -> "ChainableOp[P, float]":
        """
        Divise la sortie du pipeline par une valeur (division entière).

        Example:
            >>> import pychain as pc
            >>> pc.op().floordiv(3)(10)
            3
        """
        ...

    def sub_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Soustrait la sortie du pipeline d'une valeur (soustraction inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().sub_r(10)(5)
            5
        """
        ...

    def truediv_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Divise une valeur par la sortie du pipeline (division réelle inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().truediv_r(10)(2)
            5.0
        """
        ...

    def floordiv_r(self, value: R) -> "ChainableOp[P, R]":
        """
        Divise une valeur par la sortie du pipeline (division entière inversée).

        Example:
            >>> import pychain as pc
            >>> pc.op().floordiv_r(10)(3)
            3
        """
        ...

    def mod(self, value: R) -> "ChainableOp[P, R]":
        """
        Calcule le modulo de la sortie du pipeline par une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().mod(3)(10)
            1
        """
        ...

    def pow(self, value: R) -> "ChainableOp[P, R]":
        """
        Élève la sortie du pipeline à la puissance d'une valeur.

        Example:
            >>> import pychain as pc
            >>> pc.op().pow(2)(3)
            9
        """
        ...

    def neg(self) -> "ChainableOp[P, R]":
        """
        Applique la négation à la sortie du pipeline.

        Example:
            >>> import pychain as pc
            >>> pc.op().neg()(5)
            -5
        """
        ...

    def round_to(self, ndigits: int) -> "ChainableOp[P, float]":
        """
        Arrondit la sortie du pipeline au nombre de décimales spécifié.

        Example:
            >>> import pychain as pc
            >>> pc.op().round_to(2)(3.14159)
            3.14
        """
        ...

    def and_(self, *others: Callable[[P], bool]) -> "ChainableOp[P, bool]":
        """
        Chains multiple boolean operations using a logical AND.

        This method takes one or more other callable operations and returns a new
        ChainableOp.

        When this new operation is called with a value, it will
        return True only if the original operation and all the other
        operations return True.

        Example:
            >>> import pychain as pc
            >>> pc.op(int).gt(5).and_(pc.op().lt(10), pc.op().gt(2))(7)
            True
        """
        ...
    def is_true(self) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est "truthy".

        Example:
            >>> import pychain as pc
            >>> pc.op().is_true()(1)
            True
        """
        ...

    def is_none(self) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est None.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_none()(None)
            True
        """
        ...

    def is_not_none(self) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline n'est pas None.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_not_none()(5)
            True
        """
        ...

    def is_in(self, values: Container[R]) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est dans le conteneur fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_in([1, 2, 3])(2)
            True
        """
        ...

    def is_not_in(self, values: Container[R]) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline n'est pas dans le conteneur fourni.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_not_in([1, 2, 3])(4)
            True
        """
        ...

    def is_iterable(self) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est un itérable.

        Example:
            >>> import pychain as pc
            >>> pc.op().is_iterable()([1, 2, 3])
            True
        """
        ...

    def eq(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().eq(5)(5)
            True
        """
        ...

    def ne(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est différente de la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().ne(5)(3)
            True
        """
        ...

    def gt(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est strictement supérieure à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().gt(3)(5)
            True
        """
        ...

    def ge(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est supérieure ou égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().ge(5)(5)
            True
        """
        ...

    def lt(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est strictement inférieure à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().lt(5)(3)
            True
        """
        ...

    def le(self, value: R) -> "ChainableOp[P, bool]":
        """
        Vérifie si la sortie du pipeline est inférieure ou égale à la valeur fournie.

        Example:
            >>> import pychain as pc
            >>> pc.op().le(5)(5)
            True
        """
        ...
