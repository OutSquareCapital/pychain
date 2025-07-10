import doctest
import sys
import src.pychain._constructors as _constructors
import src.pychain._interfaces._core as _core
import src.pychain._interfaces._dict_base as _dict_base
import src.pychain._executors as _executors
import src.pychain._main as _main
import src.pychain._interfaces._iter_base as _iter_base


def run_all_doctests() -> None:
    """
    Test all doctest examples in the pychain library.
    Run with: python test_doctest.py
    """
    modules = [
        _core,
        _iter_base,
        _dict_base,
        _main,
        _executors,
        _constructors,
    ]
    failures = 0
    for mod in modules:
        print(f"\nTesting doctests in {mod.__name__}...")
        result = doctest.testmod(mod, verbose=False)
        failures += result.failed
        if failures > 0:
            print(f"\nSome doctests failed. ❌ ({failures} failures)")
            sys.exit(1)
    print("\nAll doctests passed! ✅")


if __name__ == "__main__":
    run_all_doctests()
