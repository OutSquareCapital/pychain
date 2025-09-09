# pychain

## Installation

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Testing

```bash
uv run tests/doctests.py
```

## Overview

PyChain is a Python library that provides functional-style chaining operations for data structures.

Most of the computations are done with implementations from the cytoolz library.
<https://github.com/pytoolz/cytoolz>

The stubs used for the developpement can be found here:
<https://github.com/py-stubs/cytoolz-stubs>

## Core Classes

`Iter`, `List`, and `Dict` are wrapper around their respective python collections that provides chainable operations.

```python
import pychain as pc

# Create a list with chainable operations

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

```
