# Configuration file for the Sphinx documentation builder.
import sys
from pathlib import Path

# Add source code to path
sys.path.insert(0, str(Path(__file__).parents[2].joinpath("src")))

# Project information
project = "pychain"
copyright = "2025"
author = "Thibaud Stettler"

# Extensions
extensions = [
    "sphinx.ext.autodoc",  # Pour documenter automatiquement le code
    "sphinx.ext.viewcode",  # Pour lier la documentation au code source
    "sphinx.ext.napoleon",  # Pour les docstrings en format Google/NumPy
    "sphinx_markdown_builder",  # Pour la sortie en markdown
]

# The suffix of source filenames
source_suffix = {
    ".rst": "restructuredtext",
}

# autodoc settings
autodoc_member_order = "bysource"  # Garde l'ordre du code source
autodoc_typehints = "description"  # Affiche les types dans la description
