from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .._core import CommonBase, dict_factory

if TYPE_CHECKING:
    from ._main import Dict


class IODict[K, V](CommonBase[dict[K, V]]):
    def read_json(self, filepath: Path | str) -> Dict[Any, Any]:
        return dict_factory(json.loads(Path(filepath).read_text(encoding="utf-8")))

    def write_json(self, filepath: Path | str) -> None:
        Path(filepath).write_text(json.dumps(self._data), encoding="utf-8")
