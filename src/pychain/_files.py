import hashlib
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class Metadata(TypedDict):
    source_hash: str
    created_at_utc: str
    original_path: str


def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".pychain_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def get_source_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def create_metadata(path: Path, source_hash: str) -> Metadata:
    return Metadata(
        source_hash=source_hash,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        original_path=str(path.absolute()),
    )


def prepare_cache(path: Path, source: str) -> None:
    source_hash = get_source_hash(source)
    cache_dir = get_cache_dir()
    marker_path = cache_dir / f"{source_hash}.json"
    print(f"Preparing cache for {path} with hash {source_hash[:8]} at {marker_path}...")
    if marker_path.exists():
        print(
            f"INFO: Function is identical to a previously saved version (hash: {source_hash[:8]}). Skipping file write."
        )
        return
    path.write_text(source, encoding="utf-8")
    print(f"Pipeline saved to {path.absolute()}")
    metadata = create_metadata(path, source_hash)
    marker_path.write_text(json.dumps(metadata, indent=4))


def create_setup_file(target_file: Path) -> None:
    setup_content = f"""
from setuptools import setup
from Cython.Build import cythonize

# Commande pour compiler:
# python {target_file.parent.resolve() / "setup.py"} build_ext --inplace

setup(
    ext_modules=cythonize("{target_file.name}"),
)
"""
    setup_path = target_file.parent / "setup.py"
    setup_path.write_text(textwrap.dedent(setup_content.strip()))
    print(f"Build file created at {setup_path.absolute()}")
    print(f"--> To compile, run: python {setup_path.name} build_ext --inplace")
