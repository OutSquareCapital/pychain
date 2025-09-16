import numpy as np

import pychain as pc


def check_slots() -> None:
    data = (1, 2, 3)
    iter_cls = pc.Iter(data)
    dct_cls = pc.Dict({1: "a", 2: "b", 3: "c"})
    arr_cls = pc.Array(np.array(data))
    assert not getattr(iter_cls, "__dict__", False)
    assert not getattr(dct_cls, "__dict__", False)
    assert not getattr(arr_cls, "__dict__", False)


def check_iter() -> None:
    assert (
        pc.Iter((1, 2, 3, 4))
        .filter(func=lambda x: x % 2 == 0)
        .map(func=lambda x: x * 10)
        .to_list()
        .unwrap()
    ) == [20, 40]


def check_dict() -> None:
    assert (
        pc.Dict({"a": 1, "b": 2, "c": 3})
        .filter_values(lambda v: v > 1)
        .map_values(lambda v: v * 10)
        .unwrap()
    ) == {"b": 20, "c": 30}


def check_array() -> None:
    arr: np.typing.NDArray[np.int_] = pc.iter_range(1, 10).pipe_unwrap(np.array)
    pc.Array(arr).pipe_chain(lambda x: x + 2, lambda x: x * 3).pipe_into(
        lambda x: x.clip(10, 20)
    )


if __name__ == "__main__":
    check_slots()
    check_iter()
    check_dict()
    check_array()
    print("All checks passed! ✅")
