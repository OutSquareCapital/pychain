# Contributing to pyochain

## type-checking

pyochain has been developped with pylance strict type-checking mode and Ruff for formatting.
No errors should be existing before committing new code.

## Linting and Formatting

pyochain uses Ruff for linting and formatting, with the VSCode extension.
Or you can simply run Ruff at the root.

## Architecture

The codebase is organized into several modules, each responsible for different aspects of the library:

- _core/: Core primitives shared across all wrappers
  - _main.py: CommonBase, Wrapper, Pipeable and base wrappers (IterWrapper, MappingWrapper).
  - _protocols.py: typing protocols and helper types (e.g., SupportsKeysAndGetItem).
  - __init__.py: re-exports for public surface.
- _iter/: Contains the Iter class and its associated methods.
- _dict/: Contains the Dict class and its associated methods.

### Structure of _iter and_dict Packages

Each of these packages is further divided into modules based on the type of operations they provide:

- _constructors.py: Methods for creating new instances from various data sources.
- _*.py: Categories of methods (e.g.,_aggregations.py, _rolling.py,_maps.py, ...).
- _main.py: The main public class that mixes in the other modules, implements apply/into policy, and provides utility not fitting a specific category.
- Expressions for Dict: _exprs.py with Expr/key helpers; compute_exprs is used by Dict.select and Dict.with_fields.

The __init__.py file of each package only imports the main class from _main.py to expose it at the package level.

This architecture allows for a clear separation of concerns, making the codebase easier to navigate and maintain, whilst still maintaining a public API that is easy to use.

#### Note on mixins vs composition

The choice of using mixins (multiple inheritance) over composition (having instances of other classes as attributes) was made to provide a more seamless and intuitive API for users.

This way, users can access all methods directly from the main class without needing to navigate through multiple layers of objects.

HOWEVER, Iter.struct property is a namespace composition, as it is in fact the methods of Dict that are exposed on Iter.

## Setup

After cloning the repo, run:

```bash
uv sync --dev
```

## Testing

```bash
uv run tests/doctests.py
```
