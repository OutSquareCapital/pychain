import numpy as np
import polars as pl

import pychain as pc


def basic_example() -> None:
    result = (
        pc.from_range(1, 6)  # [1, 2, 3, 4, 5]
        .map(pc.op.mul(2))  # [2, 4, 6, 8, 10]
        .filter(pc.op.gt(5))  # [6, 8, 10]
        .cumsum()  # [6, 14, 24]
        .to_list()  # [6, 14, 24]
    )
    assert result == [6, 14, 24]


def data_agg_and_transform() -> None:
    from collections import defaultdict
    from typing import NamedTuple

    class DataRow(NamedTuple):
        category: str
        value: int

    data: list[DataRow] = [
        DataRow("A", 10),
        DataRow("B", 20),
        DataRow("A", 30),
        DataRow("B", 40),
    ]

    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for row in data:
        grouped[row.category].append(row.value)

    py_result: dict[str, int] = {k: sum(v) for k, v in grouped.items()}

    chain_result: dict[str, int] = (
        pc.Iter(data)
        .group_by(lambda d: d.category)
        .map_values(lambda v: pc.Iter(v).map(lambda x: x.value).agg(sum))
        .unwrap()
    )
    assert py_result == chain_result == {"A": 40, "B": 60}


def grouping_and_reducing() -> None:
    words: list[str] = ["apple", "banana", "apricot", "blueberry", "avocado"]

    result = pc.Iter(words).group_by(on=pc.op.item(0)).map_values(len).unwrap()
    assert result == {"a": 3, "b": 2}


def nested_chaining_with_dictchain() -> None:
    data: dict[str, list[int]] = {
        "a": [1, 2, 3],
        "b": [4, 5, 6],
    }

    result: dict[str, list[int]] = (
        pc.Struct(data).map_values(lambda v: pc.Iter(v).cumsum().to_list()).unwrap()
    )
    assert result == {"a": [1, 3, 6], "b": [4, 9, 15]}


def get_polars_frame() -> None:
    results: dict[str, np.ndarray] = {
        "Library1": np.array([[1, 2, 3], [4, 5, 6]]),
        "Library2": np.array([[7, 8, 9], [10, 11, 12]]),
    }

    df = pl.DataFrame(
        data=pc.Struct(results)
        .unpivot(
            key_name="Library",
            index_name="Index",
            value_name="Values",
            value_extractor=lambda arr: arr[:, 0],
        )
        .unwrap()
    )

    df2 = pl.DataFrame(
        {
            "Library": [
                lib for lib in results.keys() for _ in range(results[lib].shape[0])
            ],
            "Index": [
                i for lib in results.keys() for i in range(results[lib].shape[0])
            ],
            "Values": [value for lib in results.keys() for value in results[lib][:, 0]],
        }
    )
    assert df.equals(df2)


if __name__ == "__main__":
    basic_example()
    data_agg_and_transform()
    grouping_and_reducing()
    nested_chaining_with_dictchain()
    get_polars_frame()
    print("All examples executed successfully.")
