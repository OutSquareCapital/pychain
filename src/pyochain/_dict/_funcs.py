from typing import Any


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
