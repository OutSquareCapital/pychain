from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Final, get_type_hints


@dataclass(slots=True)
class TypeTracker:
    p_type: Final[type]
    r_type: type

    def update(self, obj: Any) -> None:
        match obj:
            case func if callable(func) and not isinstance(func, type):
                self._handle_callable(func)

            case t if isinstance(t, type):
                self._update(t)

            case _:
                self._update(type(obj))

    def _update(self, obj: Any) -> None:
        self.r_type = obj
        print(f"DEBUG: Updated return type to {self.r_type}")

    def _handle_callable(self, func: Callable[..., Any]) -> None:
        hints = get_type_hints(func)
        if return_type := hints.get("return"):
            self._update(return_type)
        else:
            self._update(object)
