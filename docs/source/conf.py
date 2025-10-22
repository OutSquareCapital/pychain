# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# Permet à Sphinx de trouver votre code source dans le dossier 'src'
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pychain"
copyright = "2025, thibaud"
author = "thibaud"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# AJOUTEZ VOS EXTENSIONS ICI
extensions = [
    "sphinx.ext.autodoc",  # Le coeur de la génération depuis les docstrings
    "sphinx.ext.napoleon",  # Pour comprendre les docstrings style Google
    "sphinx.ext.viewcode",  # Pour ajouter des liens vers le code source
    "sphinx_autodoc_typehints",  # Pour afficher les type hints
    "sphinx.ext.doctest",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# DÉFINISSEZ LE THÈME ICI
html_theme = "furo"
html_static_path = ["_static"]
