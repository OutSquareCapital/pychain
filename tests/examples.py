import numpy as np

import pychain as pc


def check_slots():
    data = (1, 2, 3)
    seq_cls = pc.Seq(data)
    mut_seq_cls = pc.SeqMut(data)
    iter_cls = pc.Iter(data)
    dct_cls = pc.Dict({1: "a", 2: "b", 3: "c"})
    assert not getattr(seq_cls, "__dict__", False)
    assert not getattr(mut_seq_cls, "__dict__", False)
    assert not getattr(iter_cls, "__dict__", False)
    assert not getattr(dct_cls, "__dict__", False)


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
        pc.Array[np.int64](np.array(data))
        .pipe(lambda x: x + 2)
        .to_iter()
        .map(lambda x: x + 2)
        .println()
        .peekn(2)
        .println()
        .to_list()
        .println()
    )


if __name__ == "__main__":
    check_slots()
    check_iter()
    check_dict()
    check_array()
