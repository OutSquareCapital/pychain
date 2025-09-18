from pathlib import Path

import pdoc
import pdoc.render

# Import le module pour s'assurer que les namespaces sont correctement exposés

# Générer la documentation avec pdoc
modules = ["pychain._iter"]
pdoc.render.configure(
    docformat="markdown",
    template_directory=None,
    show_source=False,
)
pdoc.pdoc(*modules, output_directory=Path("docs"))

print("Documentation générée avec succès dans le dossier 'docs'.")
