from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import cytoolz as cz

from .._core import MappingWrapper

if TYPE_CHECKING:
    from ._main import Dict


class GroupsDict[K, V](MappingWrapper[K, V]):
    def group_by_value[G](self, func: Callable[[V], G]) -> Dict[G, dict[K, V]]:
        """
        Group dict items into sub-dictionaries based on a function of the value.

        >>> import pychain as pc
        >>> d = {"a": 1, "b": 2, "c": 3, "d": 2}
        >>> pc.Dict(d).group_by_value(lambda v: v % 2).unwrap()
        {1: {'a': 1, 'c': 3}, 0: {'b': 2, 'd': 2}}
        """
        return self.apply(
            lambda data: cz.dicttoolz.valmap(
                dict, cz.itertoolz.groupby(lambda kv: func(kv[1]), data.items())
            )
        )

    def group_by_key[G](self, func: Callable[[K], G]) -> Dict[G, dict[K, V]]:
        """
        Group dict items into sub-dictionaries based on a function of the key.

        >>> import pychain as pc
        >>> d = {"user_1": 10, "user_2": 20, "admin_1": 100}
        >>> pc.Dict(d).group_by_key(lambda k: k.split("_")[0]).unwrap()
        {'user': {'user_1': 10, 'user_2': 20}, 'admin': {'admin_1': 100}}
        """
        return self.apply(
            lambda data: cz.dicttoolz.valmap(
                dict, cz.itertoolz.groupby(lambda kv: func(kv[0]), data.items())
            )
        )

    def group_by_key_agg[G, R](
        self,
        key_func: Callable[[K], G],
        agg_func: Callable[[Dict[K, V]], R],
    ) -> Dict[G, R]:
        """
        Group by key function, then apply aggregation function to each sub-dict.

        This avoids materializing intermediate `Dict` objects if you only need
        an aggregated result for each group.

        >>> import pychain as pc
        >>>
        >>> data = {"user_1": 10, "user_2": 20, "admin_1": 100}
        >>> pc.Dict(data).group_by_key_agg(
        ...     key_func=lambda k: k.split("_")[0],
        ...     agg_func=lambda d: d.iter_values().sum(),
        ... ).unwrap()
        {'user': 30, 'admin': 100}
        >>>
        >>> data_files = {
        ...     "file_a.txt": 100,
        ...     "file_b.log": 20,
        ...     "file_c.txt": 50,
        ...     "file_d.log": 5,
        ... }
        >>>
        >>> def get_stats(sub_dict: pc.Dict[str, int]) -> dict[str, Any]:
        ...     return {
        ...         "count": sub_dict.iter_keys().length(),
        ...         "total_size": sub_dict.iter_values().sum(),
        ...         "max_size": sub_dict.iter_values().max(),
        ...         "files": sub_dict.iter_keys().sort().into(list),
        ...     }
        >>>
        >>> pc.Dict(data_files).group_by_key_agg(
        ...     key_func=lambda k: k.split(".")[-1], agg_func=get_stats
        ... ).sort().unwrap()
        {'log': {'count': 2, 'total_size': 25, 'max_size': 20, 'files': ['file_b.log', 'file_d.log']}, 'txt': {'count': 2, 'total_size': 150, 'max_size': 100, 'files': ['file_a.txt', 'file_c.txt']}}
        """
        from ._main import Dict

        def _(data: dict[K, V]) -> dict[G, R]:
            groups = cz.itertoolz.groupby(lambda kv: key_func(kv[0]), data.items())
            return cz.dicttoolz.valmap(
                lambda items: agg_func(Dict(dict(items))), groups
            )

        return self.apply(_)

    def group_by_value_agg[G, R](
        self,
        value_func: Callable[[V], G],
        agg_func: Callable[[Dict[K, V]], R],
    ) -> Dict[G, R]:
        """
        Group by value function, then apply aggregation function to each sub-dict.

        This avoids materializing intermediate `Dict` objects if you only need
        an aggregated result for each group.

        >>> import pychain as pc
        >>>
        >>> data = {"math": "A", "physics": "B", "english": "A"}
        >>> pc.Dict(data).group_by_value_agg(
        ...     value_func=lambda grade: grade,
        ...     agg_func=lambda d: d.iter_keys().length(),
        ... ).unwrap()
        {'A': 2, 'B': 1}
        >>>
        >>> # --- Exemple 2: Agrégation plus complexe ---
        >>> sales_data = {
        ...     "store_1": "Electronics",
        ...     "store_2": "Groceries",
        ...     "store_3": "Electronics",
        ...     "store_4": "Clothing",
        ... }
        >>>
        >>> # Obtain the first store for each category (after sorting store names)
        >>> pc.Dict(sales_data).group_by_value_agg(
        ...     value_func=lambda category: category,
        ...     agg_func=lambda d: d.iter_keys().sort().first(),
        ... ).sort().unwrap()
        {'Clothing': 'store_4', 'Electronics': 'store_1', 'Groceries': 'store_2'}
        """
        from ._main import Dict

        def _(data: dict[K, V]) -> dict[G, R]:
            groups = cz.itertoolz.groupby(lambda kv: value_func(kv[1]), data.items())
            return cz.dicttoolz.valmap(
                lambda items: agg_func(Dict(dict(items))), groups
            )

        return self.apply(_)
