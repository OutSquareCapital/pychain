from collections.abc import Callable, Iterable
from typing import Any

type CheckFunc[T] = Callable[[T], bool]
type ProcessFunc[T] = Callable[[T], T]
type TransformFunc[T, T1] = Callable[[T], T1]
type AggFunc[V, V1] = Callable[[Iterable[V]], V1]
type ThreadFunc[T] = Callable[..., T] | tuple[Callable[..., T], Any]
