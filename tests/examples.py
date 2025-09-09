import numpy as np

import pychain as pc

assert (
    pc.Iter((1, 2, 3, 4))
    .filter(func=lambda x: x % 2 == 0)
    .map(func=lambda x: x * 10)
    .into_list()
    .unwrap()
) == [20, 40]
# Transform dict contents
assert (
    pc.Dict({"a": 1, "b": 2, "c": 3})
    .filter(lambda v: v > 1)
    .map_values(lambda v: v * 10)
    .unwrap()
) == {"b": 20, "c": 30}


print(pc.Array[np.int64](np.array([1, 2, 3, 4])).add(2))
