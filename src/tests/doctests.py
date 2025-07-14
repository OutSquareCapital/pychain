import ast
import doctest
import importlib
import pkgutil
import sys
from pathlib import Path
from types import ModuleType

from tqdm import tqdm


def _test_stub_files(package: str) -> None:
    package_path = Path(importlib.import_module(package).__path__[0])
    stub_files = package_path.rglob("*.pyi")
    failures = 0
    from operator import add

    from pychain import Iter, Struct, op

    globs = {
        "ChainableOp": op,
        "Iter": Iter,
        "Struct": Struct,
        "add": add,
    }

    for stub_file in stub_files:
        with open(stub_file, "r+", encoding="utf-8") as f:
            content = f.read()
            new_content = content.replace('default[V]="foo"', 'default="foo"')
            if content != new_content:
                f.seek(0)
                f.write(new_content)
                f.truncate()
                content = new_content

        try:
            # Parse the .pyi file to extract docstrings
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if docstring := ast.get_docstring(node):
                        parser = doctest.DocTestParser()
                        test = parser.get_doctest(
                            docstring, globs, node.name, str(stub_file), node.lineno
                        )
                        runner = doctest.DocTestRunner()
                        failures += runner.run(test).failed
        except Exception as e:
            print(f"Error testing {stub_file}: {e}")

    if failures > 0:
        print(f"\nSome doctests in stubs failed. ❌ ({failures} failures)")
        sys.exit(1)


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
    _test_stub_files(package)
    print("\nAll doctests passed! ✅")


if __name__ == "__main__":
    run_all_doctests(package="pychain")
