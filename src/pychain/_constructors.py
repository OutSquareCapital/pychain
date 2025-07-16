from collections.abc import Callable
from typing import Any

from ._exprs import When

def when[T, R](predicate: Callable[[T], bool]) -> When[T, Any]:
    return When[T, R](predicate)

