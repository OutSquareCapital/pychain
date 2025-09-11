import numpy as np

import pychain as pc


def check_iter():
    assert (
        pc.Iter((1, 2, 3, 4))
        .filter(func=lambda x: x % 2 == 0)
        .map(func=lambda x: x * 10)
        .to_list()
        .unwrap()
    ) == [20, 40]


def check_dict():
    assert (
        pc.Dict({"a": 1, "b": 2, "c": 3})
        .filter_values(lambda v: v > 1)
        .map_values(lambda v: v * 10)
        .unwrap()
    ) == {"b": 20, "c": 30}


def check_array():
    data = pc.Iter.from_range(1, 10).unwrap()
    (
        pc.Array(np.array(data))
        .add(2)
        .to_iter()
        .map(lambda x: x + 2)
        .println()
        .peekn(2)
        .println()
        .to_list()
        .println()
    )


if __name__ == "__main__":
    check_iter()
    check_dict()
    check_array()
