from collections.abc import Mapping
from typing import Any

import cytoolz as cz


def schema_recursive(data: dict[Any, Any], max_depth: int) -> Any:
    def _recurse_schema(node: Any, current_depth: int) -> Any:
        if isinstance(node, dict):
            if current_depth >= max_depth:
                return "dict"
            return {
                k: _recurse_schema(v, current_depth + 1)
                for k, v in node.items()  # type: ignore
            }
        elif cz.itertoolz.isiterable(node):
            if current_depth >= max_depth:
                return type(node).__name__
            return _recurse_schema(cz.itertoolz.first(node), current_depth + 1)
        else:
            return type(node).__name__

    return _recurse_schema(data, 0)


def flatten_recursive(
    data: dict[Any, Any], sep: str, max_depth: int | None
) -> dict[str, Any]:
    def _(
        d: dict[Any, Any], parent_key: str = "", current_depth: int = 1
    ) -> dict[str, Any]:
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict) and (
                max_depth is None or current_depth < max_depth + 1
            ):
                items.extend(
                    _(v, new_key, current_depth + 1).items()  # type: ignore
                )
            else:
                items.append((new_key, v))  # type: ignore
        return dict(items)

    return _(data)


def difference[K, V](
    data: Mapping[K, V], other: Mapping[K, V]
) -> dict[K, tuple[V | None, V | None]]:
    all_keys: set[K] = data.keys() | other.keys()
    diffs: dict[K, tuple[V | None, V | None]] = {}
    for key in all_keys:
        self_val = data.get(key)
        other_val = other.get(key)
        if self_val != other_val:
            diffs[key] = (self_val, other_val)
    return diffs


def dict_repr(
    v: object,
    depth: int = 0,
    max_depth: int = 3,
    max_items: int = 6,
    max_str: int = 80,
    indent: int = 2,
) -> str:
    pad = " " * (depth * indent)
    if depth > max_depth:
        return "…"
    match v:
        case dict():
            items: list[tuple[str, Any]] = list(v.items())  # type: ignore
            shown: list[tuple[str, Any]] = items[:max_items]
            if (
                all(
                    not isinstance(val, dict) and not isinstance(val, list)
                    for _, val in shown
                )
                and len(shown) <= 2
            ):
                body = ", ".join(
                    f"{k!r}: {dict_repr(val, depth + 1)}" for k, val in shown
                )
                if len(items) > max_items:
                    body += ", …"
                return "{" + body + "}"
            lines: list[str] = []
            for k, val in shown:
                lines.append(
                    f"{pad}{' ' * indent}{k!r}: {dict_repr(val, depth + 1, max_depth, max_items, max_str, indent)}"
                )
            if len(items) > max_items:
                lines.append(f"{pad}{' ' * indent}…")
            return "{\n" + ",\n".join(lines) + f"\n{pad}" + "}"

        case list():
            elems: list[Any] = v[:max_items]  # type: ignore
            if (
                all(isinstance(x, (int, float, str, bool, type(None))) for x in elems)
                and len(elems) <= 4
            ):
                body = ", ".join(dict_repr(x, depth + 1) for x in elems)
                if len(v) > max_items:  # type: ignore
                    body += ", …"
                return "[" + body + "]"
            lines = [
                f"{pad}{' ' * indent}{dict_repr(x, depth + 1, max_depth, max_items, max_str, indent)}"
                for x in elems
            ]
            if len(v) > max_items:  # type: ignore
                lines.append(f"{pad}{' ' * indent}…")
            return "[\n" + ",\n".join(lines) + f"\n{pad}" + "]"

        case str():
            return repr(v if len(v) <= max_str else v[:max_str] + "…")
        case _:
            return repr(v)
