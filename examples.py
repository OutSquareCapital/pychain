import src.pychain as pc
import polars as pl
import numpy as np

def basic_example() -> None:
    result = (
        pc.from_range(1, 6)  # [1, 2, 3, 4, 5]
        .map(lambda x: x * 2)  # [2, 4, 6, 8, 10]
        .filter(lambda x: x > 5)  # [6, 8, 10]
        .cumsum()  # [6, 14, 24]
        .convert_to.list()  # [6, 14, 24]
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
        pc.IterChain(data)
        .into_groups(lambda d: d.category)
        .map_values(lambda v: v.map(lambda d: d.value).agg(sum).unwrap())
        .unwrap()
    )
    assert py_result == chain_result == {'A': 40, 'B': 60}

def grouping_and_reducing() -> None:

    words: list[str] = ["apple", "banana", "apricot", "blueberry", "avocado"]

    result = (
        pc.IterChain(words)
        .into_groups(lambda w: w[0])  # group by first letter
        .map_values(lambda chain: chain.agg(len).unwrap())  # type: ignore
        .unwrap()
    )
    assert result == {'a': 3, 'b': 2}

def nested_chaining_with_dictchain() -> None:
        
    data: dict[str, list[int]] = {
        "a": [1, 2, 3],
        "b": [4, 5, 6],
    }

    result: dict[str, list[int]] = (
        pc.DictChain(data)
        .map_values(lambda chain: pc.IterChain(chain).cumsum().convert_to.list())
        .unwrap()
    )
    assert result == {'a': [1, 3, 6], 'b': [4, 9, 15]}

def get_polars_frame() -> None:
    results: dict[str, np.ndarray] = {
        "Library1": np.array([[1, 2, 3], [4, 5, 6]]),
        "Library2": np.array([[7, 8, 9], [10, 11, 12]]),
    }
    df = pl.DataFrame(
        data=pc.DictChain(results)
        .unpivot(
            key_name="Library",
            index_name="Index",
            value_name="Values",
            value_extractor=lambda arr: arr[:, 0]
        )
        .convert_to.dataframe()
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