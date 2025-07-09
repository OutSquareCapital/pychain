import doctest
import sys

import src.pychain._constructors as constructors
import src.pychain._core as core
import src.pychain._dict_base as dict_base
import src.pychain._executors as executors
import src.pychain._implementations as implementations
import src.pychain._iter_base as iter_base
import src.pychain._lazyfuncs as lazyfuncs


def run_all_doctests() -> None:
    """
    Test all doctest examples in the pychain library.
    Run with: python test_doctest.py
    """
    modules = [
        lazyfuncs,
        core,
        iter_base,
        dict_base,
        implementations,
        executors,
        constructors,
    ]
    failures = 0
    for mod in modules:
        print(f"\nTesting doctests in {mod.__name__}...")
        result = doctest.testmod(mod, verbose=False)
        failures += result.failed
        if failures == 0:
            print("\nAll doctests passed! ✅")
        else:
            print(f"\nSome doctests failed. ❌ ({failures} failures)")
            sys.exit(1)


if __name__ == "__main__":
    run_all_doctests()
