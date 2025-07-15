from collections.abc import Callable
from typing import Any

from ._exprs import OpConstructor, When
from ._iter import IterConstructor
from ._struct import StructConstructor


def when[T, R](predicate: Callable[[T], bool]) -> When[T, Any]:
    return When[T, R](predicate)


op = OpConstructor()
iter = IterConstructor()
struct = StructConstructor()
