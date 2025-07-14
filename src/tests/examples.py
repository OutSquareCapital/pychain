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
        pc.Struct(pc.Iter(data)
        .group_by(lambda d: d.category))
        .map_values(lambda v: pc.Iter(v).map(lambda x: x.value).agg(sum))
        .unwrap()
    )
    assert py_result == chain_result == {"A": 40, "B": 60}


def grouping_and_reducing() -> None:
    words: list[str] = ["apple", "banana", "apricot", "blueberry", "avocado"]

    result = pc.Iter(words).group_by(on=pc.op.item(0))
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

if __name__ == "__main__":
    basic_example()
    data_agg_and_transform()
    grouping_and_reducing()
    nested_chaining_with_dictchain()
    print("All examples executed successfully.")
