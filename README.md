# pychain

pychain is a Python library that provides functional-style chaining operations for data structures.

## Overview

### Primary Goal

To provide a fluent, declarative, and functional method-chaining API for data manipulation in Python.

### Philosophy

Eliminate imperative loops (`for`, `while`) in favor of a sequence of high-level operations.

Each method transforms the data and returns a new wrapper instance, enabling continuous chaining until a terminal method is called to extract the result.

### Key Dependencies and credits

Most of the computations are done with implementations from the `cytoolz`, `more-itertools`, and `rolling` libraries.

An extensive use of the `itertools` stdlib module is also to be noted.

pychain acts as a unifying API layer over these powerful tools.

<https://github.com/pytoolz/cytoolz>

<https://github.com/more-itertools/more-itertools>

<https://github.com/ajcr/rolling>

The stubs used for the developpement, made by the maintainer of pychain, can be found here:

<https://github.com/py-stubs/cytoolz-stubs>

### Design

Based on wrapper classes that encapsulate native Python data structures or third-party library objects.

* **`Iter[T]`**: For any `Iterable`. This is the most generic and powerful wrapper. Most operations are **lazy**.
* **`Dict[KT, VT]`**: For `dict` objects.
* **`Wrapper[T]`**: For Any object.

**Note on `Wrapper`**:

The primary goal of this class is to allow the user of pychain to keep a consistent method-chaining style across their codebase, even when working with objects that do not support this style (eg. numpy arrays, pure functions, ...).
It does however not provide any additional functionality beyond the `pipe` methods family, and the convenience `to_iter` and `to_dict` methods.

### Interoperability

Designed to integrate seamlessly with other data manipulation libraries, like `polars`, using the `pipe_into` and `unwrap` methods.

### Typing

Each method and class make extensive use of generics, type hints, and overloads (when necessary) to ensure type safety and improve developer experience.

Since there's much less need for intermediate variables, the developper don't have to annotate them as much, whilst still keeping a type-safe codebase.

## Real-life simple example

In one of my project, I have to introspect some modules from plotly to get some lists of colors.

I want to check wether the colors are in hex format or not, and I want to get a dictionary of palettes.
We can see here that pychain allow to keep the same style than polars, with method chaining, but for plain python objects.

Due to the freedom of python, multiple paradigms are implemented across libraries. If you like the fluent, functional, chainable style, pychain can help you to keep it across your codebase, rather than mixing object().method().method() and then another where it's [[... for ... in ...] ... ].

```python

from types import ModuleType

import polars as pl
import pychain as pc
from plotly.express.colors import cyclical, qualitative, sequential



MODULES: set[ModuleType] = {
    sequential,
    cyclical,
    qualitative,
}


def get_palettes() -> pc.Dict[str, list[str]]:
    clr = "color"
    scl = "scale"
    df: pl.DataFrame = (
        pc.Iter(MODULES)
        .map(
            lambda mod: pc.dict_of(mod)
            .filter_values(lambda v: isinstance(v, list))
            .unwrap()
        )
        .pipe_unwrap(pl.LazyFrame)
        .unpivot(value_name=clr, variable_name=scl)
        .drop_nulls()
        .filter(
            pl.col(clr)
            .list.eval(pl.element().first().str.starts_with("#").alias("is_hex"))
            .list.first()
        )
        .sort(scl)
        .collect()
    )
    keys: list[str] = df.get_column(scl).to_list()
    values: list[list[str]] = df.get_column(clr).to_list()
    return pc.dict_zip(keys, values)

# Ouput excerpt:
{'mygbm_r': ['#ef55f1',
            '#c543fa',
            '#9139fa',
            '#6324f5',
            '#2e21ea',
            '#284ec8',
            '#3d719a',
            '#439064',
            '#31ac28',
            '#61c10b',
            '#96d310',
            '#c6e516',
            '#f0ed35',
            '#fcd471',
            '#fbafa1',
            '#fb84ce',
            '#ef55f1']}
```

However you can still easily go back with for loops when the readability is better this way.

In another place, I use this function to generate a Literal from the keys of the palettes.

```python

from enum import StrEnum

class Text(StrEnum):
    CONTENT = "Palettes = Literal[\n"
    END_CONTENT = "]\n"
    ...# rest of the class

def generate_palettes_literal() -> None:
    literal_content: str = Text.CONTENT
    for name in get_palettes().iter_keys().sort().unwrap():
        literal_content += f'    "{name}",\n'
    literal_content += Text.END_CONTENT
    ...# rest of the function
```

Since I have to reference the literal_content variable in the for loop, This is more reasonnable to use a for loop here rather than a map + reduce approach.

## Installation

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Developpement

### Setup

After cloning the repo, run:

```bash
uv sync --dev
```

### Testing

```bash
uv run tests/doctests.py
```

### Build docs

```bash
uv run scripts/build_docs.py
```
