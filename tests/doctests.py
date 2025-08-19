import doctest
import importlib
import pkgutil
import sys
from pathlib import Path
from types import ModuleType


def _get_modules(package: str) -> list[ModuleType]:
    modules: list[ModuleType] = []
    pkg: ModuleType = importlib.import_module(package)
    for _, modname, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if not ispkg:
            try:
                modules.append(importlib.import_module(modname))
            except Exception:
                pass
    return modules


def _test_modules(modules: list[ModuleType], verbose: bool) -> None:
    failures = 0
    for mod in modules:
        result = doctest.testmod(mod, verbose=verbose)
        failures += result.failed
        if failures > 0:
            print(f"\nSome doctests failed. ❌ ({failures} failures)")
            sys.exit(1)


def run_all_doctests(package: str, verbose: bool = False) -> None:
    modules: list[ModuleType] = _get_modules(package)
    _test_modules(modules, verbose)
    print("\nAll doctests passed! ✅")


def find_package_name(src_path: str) -> str:
    src = Path(src_path)
    for child in src.iterdir():
        if (
            child.is_dir()
            and (child / "__init__.py").exists()
            or (child / "__init__.pyi").exists()
        ):
            return child.name
    raise RuntimeError("No package found in src")


if __name__ == "__main__":
    package_name = find_package_name("src")
    print(f"Running doctests for package: {package_name}")
    run_all_doctests(package=package_name)
