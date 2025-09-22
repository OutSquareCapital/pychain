from __future__ import annotations

from pathlib import Path

from .._core import CommonBase


class IODict[K, V](CommonBase[dict[K, V]]):
    def write_json(self, filepath: Path | str) -> None:
        import json

        Path(filepath).write_text(json.dumps(self._data), encoding="utf-8")

    def write_csv(self, filepath: Path | str) -> None:
        import csv

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            csv.writer(csvfile).writerows(self._data.items())
        csvfile.close()

    def write_pickle(self, filepath: Path | str) -> None:
        import pickle

        Path(filepath).write_bytes(pickle.dumps(self._data))
