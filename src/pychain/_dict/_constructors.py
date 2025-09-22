from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ._main import Dict


def read_json(filepath: Path | str) -> Dict[Any, Any]:
    import json

    return Dict(json.loads(Path(filepath).read_text(encoding="utf-8")))


def read_csv(filepath: Path | str) -> Dict[str, list[str]]:
    import csv

    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
    return Dict({rows[0]: rows[1:] for rows in reader})


def read_toml(filepath: Path | str) -> Dict[str, Any]:
    import tomllib

    return Dict(tomllib.loads(Path(filepath).read_text()))


def read_pickle(filepath: Path | str) -> Dict[Any, Any]:
    import pickle

    return Dict(pickle.loads(Path(filepath).read_bytes()))


def dict_zip[K, V](keys: Iterable[K], values: Iterable[V]) -> Dict[K, V]:
    """
    Create a Dict from two iterables of keys and values.

    Syntactic sugar for `Dict(dict(zip(keys, values)))`.

    >>> dict_zip([1, 2], ["a", "b"])
    {1: 'a', 2: 'b'}
    """
    return Dict(dict(zip(keys, values)))


def dict_of(obj: object) -> Dict[str, Any]:
    """
    Create a Dict from an object's __dict__ attribute.
    Syntactic sugar for `Dict(obj.__dict__)`.

        >>> class A:
        ...     def __init__(self):
        ...         self.x = 1
        ...         self.y = 2
        >>> dict_of(A())
        {'x': 1, 'y': 2}
    """
    return Dict(obj.__dict__)
