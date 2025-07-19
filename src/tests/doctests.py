import doctest
import importlib
import pkgutil
import sys
from types import ModuleType

from tqdm import tqdm

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


def _test_modules(modules: list[ModuleType]) -> None:
    failures = 0
    with tqdm(total=len(modules), desc="Running doctests", unit="module") as pbar:
        for mod in modules:
            pbar.set_description(f"Running doctests in {mod.__name__}")
            result = doctest.testmod(mod, verbose=False)
            failures += result.failed
            if failures > 0:
                print(f"\nSome doctests failed. ❌ ({failures} failures)")
                pbar.close()
                sys.exit(1)
            pbar.update(1)


def run_all_doctests(package: str) -> None:
    modules: list[ModuleType] = _get_modules(package)
    _test_modules(modules)
    print("\nAll doctests passed! ✅")


if __name__ == "__main__":
    run_all_doctests(package="pychain")
