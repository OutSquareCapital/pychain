from collections.abc import Callable
from functools import partial
import cytoolz.itertoolz as itz
from ._functions import partial_map
from .._protocols import TransformFunc

frequencies = itz.frequencies


def group_by[K, V](on: TransformFunc[V, K]) -> partial[dict[K, list[V]]]:
    return partial(itz.groupby, on)


def reduce_by[K, V](
    key: TransformFunc[V, K], binop: Callable[[V, V], V]
) -> partial[dict[K, V]]:
    return partial(itz.reduceby, key=key, binop=binop)


def to_records(keys: list[str]):
    return partial_map(lambda row: dict(zip(keys, row)))  # type: ignore
