import doctest
import sys
import src.pychain._constructors as _constructors
import src.pychain._core as _core
import src.pychain._dict_base as _dict_base
import src.pychain._executors as _executors
import src.pychain._implementations as _implementations
import src.pychain._iter_base as _iter_base
import src.pychain._lazyfuncs as _lazyfuncs
import src.pychain._expressions.chainable as chainable


def run_all_doctests() -> None:
    """
    Test all doctest examples in the pychain library.
    Run with: python test_doctest.py
    """
    modules = [
        chainable,
        _lazyfuncs,
        _core,
        _iter_base,
        _dict_base,
        _implementations,
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
