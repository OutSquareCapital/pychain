import itertools
from collections.abc import Callable

import cytoolz as cz
from narwhals.typing import IntoDataFrame, IntoLazyFrame

from ._main import Iter


def iter_count(start: int = 0, step: int = 1) -> Iter[int]:
    """
    Create an infinite iterator of evenly spaced values.

    **Warning** ⚠️

    This creates an infinite iterator.

    Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> iter_count(10, 2).head(3).to_list()
        [10, 12, 14]
    """
    return Iter(itertools.count(start, step))


def iter_range(start: int, stop: int, step: int = 1) -> Iter[int]:
    """
    Create an iterator from a range.

    Syntactic sugar for `Iter(range(start, stop, step))`.

        >>> iter_range(1, 5).to_list()
        [1, 2, 3, 4]
    """
    return Iter(range(start, stop, step))


def iter_func[T](func: Callable[[T], T], x: T) -> Iter[T]:
    """
    Create an infinite iterator by repeatedly applying a function into an original input x.

    **Warning** ⚠️

    This creates an infinite iterator.

    Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

        >>> iter_func(lambda x: x + 1, 0).head(3).to_list()
        [0, 1, 2]
    """
    return Iter(cz.itertoolz.iterate(func, x))


def iter_col(data: IntoDataFrame | IntoLazyFrame, column: str):
    """
    Create an iterator from a column in a DataFrame or LazyFrame.

    Anything supported by narwhals will works (e.g., pandas, polars, DuckDB, etc...).

    Note that a LazyFrame input will be collected, but will only materialize the specified column.


    >>> import polars as pl
    >>> data = {"a": [1, 2, 3], "b": ["x", "y", "z"]}
    >>> pl.LazyFrame(data).pipe(iter_col, "a").to_list()
    [1, 2, 3]

    **Note for polars users**:

    This mostly give you a convenient way to avoid interrupting the method chain when going from polars to pychain.

    This method is simply syntactic sugar for:

    ```python
    Iter(df.lazy().select(column).collect().get_column(column))
    ```

    This is due to the fact that polars.Series.pipe don't (and won't) exist.

    For more details, see https://github.com/pola-rs/polars/issues/14032

    """
    import narwhals as nw

    return Iter(
        nw.from_native(data)
        .lazy()
        .select(column)
        .collect()
        .get_column(column)
        .to_native()
    )


def iter_on[T](*elements: T) -> Iter[T]:
    """
    Create an iterator from the given elements.

        >>> iter_on(1, 2, 3).to_list()
        [1, 2, 3]
    """
    return Iter(elements)
