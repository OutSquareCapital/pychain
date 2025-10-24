from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
from typing import TYPE_CHECKING, Concatenate

from .._core import IterWrapper

if TYPE_CHECKING:
    from .._dict import Dict
    from ._main import Iter


class BaseDict[T](IterWrapper[T]):
    def struct[**P, R, K, V](
        self: IterWrapper[dict[K, V]],
        func: Callable[Concatenate[Dict[K, V], P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Iter[R]:
        """
        Apply a function to each element after wrapping it in a Dict.

        This is a convenience method for the common pattern of mapping a function over an iterable of dictionaries.

        Args:
            func: Function to apply to each wrapped dictionary.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        Example:
        ```python
        >>> from typing import Any
        >>> import pyochain as pc

        >>> data: list[dict[str, Any]] = [
        ...     {"name": "Alice", "age": 30, "city": "New York"},
        ...     {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ...     {"name": "Charlie", "age": 35, "city": "New York"},
        ...     {"name": "David", "age": 40, "city": "Paris"},
        ... ]
        >>>
        >>> def to_title(d: pc.Dict[str, Any]) -> pc.Dict[str, Any]:
        ...     return d.map_keys(lambda k: k.title())
        >>> def is_young(d: pc.Dict[str, Any]) -> bool:
        ...     return d.unwrap().get("Age", 0) < 30
        >>> def set_continent(d: pc.Dict[str, Any], value: str) -> dict[str, Any]:
        ...     return d.with_key("Continent", value).unwrap()
        >>>
        >>> pc.Iter.from_(data).struct(to_title).filter_false(is_young).map(
        ...     lambda d: d.drop("Age").with_key("Continent", "NA")
        ... ).map_if(
        ...     lambda d: d.unwrap().get("City") == "Paris",
        ...     lambda d: set_continent(d, "Europe"),
        ...     lambda d: set_continent(d, "America"),
        ... ).group_by(lambda d: d.get("Continent")).map_values(
        ...     lambda d: pc.Iter.from_(d)
        ...     .struct(lambda d: d.drop("Continent").unwrap())
        ...     .into(list)
        ... )  # doctest: +NORMALIZE_WHITESPACE
        Dict({
        'America': [
            {'Name': 'Alice', 'City': 'New York'},
            {'Name': 'Charlie', 'City': 'New York'}
        ],
        'Europe': [
            {'Name': 'David', 'City': 'Paris'}
        ]
        })

        ```
        """
        from .._dict import Dict

        def _struct(data: Iterable[dict[K, V]]) -> Generator[R, None, None]:
            return (func(Dict(x), *args, **kwargs) for x in data)

        return self.apply(_struct)

    def with_keys[K](self, keys: Iterable[K]) -> Dict[K, T]:
        """
        Create a Dict by zipping the iterable with keys.

        Args:
            keys: Iterable of keys to pair with the values.
        Example:
        ```python
        >>> import pyochain as pc
        >>> keys = ["a", "b", "c"]
        >>> values = [1, 2, 3]
        >>> pc.Iter.from_(values).with_keys(keys).unwrap()
        {'a': 1, 'b': 2, 'c': 3}
        >>> # This is equivalent to:
        >>> pc.Iter.from_(keys).zip(values).pipe(
        ...     lambda x: pc.Dict(x.into(dict)).unwrap()
        ... )
        {'a': 1, 'b': 2, 'c': 3}

        ```
        """
        from .._dict import Dict

        def _with_keys(data: Iterable[T]) -> Dict[K, T]:
            return Dict(dict(zip(keys, data)))

        return self.into(_with_keys)

    def with_values[V](self, values: Iterable[V]) -> Dict[T, V]:
        """
        Create a Dict by zipping the iterable with values.

        Args:
            values: Iterable of values to pair with the keys.
        Example:
        ```python
        >>> import pyochain as pc
        >>> keys = [1, 2, 3]
        >>> values = ["a", "b", "c"]
        >>> pc.Iter.from_(keys).with_values(values).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}
        >>> # This is equivalent to:
        >>> pc.Iter.from_(keys).zip(values).pipe(
        ...     lambda x: pc.Dict(x.into(dict)).unwrap()
        ... )
        {1: 'a', 2: 'b', 3: 'c'}

        ```
        """
        from .._dict import Dict

        def _with_values(data: Iterable[T]) -> Dict[T, V]:
            return Dict(dict(zip(data, values)))

        return self.into(_with_values)
