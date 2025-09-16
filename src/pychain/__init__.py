"""

PyChain is a Python library that provides functional-style chaining operations for data structures.
Most of the computations are done with implementations from the cytoolz library.

<https://github.com/pytoolz/cytoolz>

The stubs used for the developpement can be found here:

<https://github.com/py-stubs/cytoolz-stubs>

## Overview
* **Primary Goal**: To provide a fluent, declarative, and functional method-chaining API for data manipulation in Python.

* **Philosophy**: Eliminate imperative loops (`for`, `while`) in favor of a sequence of high-level operations. Each method transforms the data and returns a new wrapper instance, enabling continuous chaining until a terminal method is called to extract the result.

* **Key Dependencies**: `itertools`, `cytoolz`, `more-itertools`, `numpy`. The library acts as a unifying and simplifying API layer over these powerful tools.

* **Design**: Based on wrapper classes that encapsulate native Python data structures or third-party library objects.

  * **`Iter[T]`**: For any `Iterable`. This is the most generic and powerful wrapper. Most operations are **lazy**.
  * **`Dict[KT, VT]`**: For `dict` objects.
  * **`Array[T]`**: For `numpy.ndarray` objects.
* **Interoperability**: Designed to integrate seamlessly with other data manipulation libraries, like `polars`, using the `pipe_into` and `unwrap` methods.
"""

from ._arrays import Array
from ._constructors import iter_count, iter_func, iter_range
from ._dict import Dict
from ._iter import Iter

__all__ = [
    "Dict",
    "Iter",
    "Array",
    "iter_count",
    "iter_func",
    "iter_range",
]
