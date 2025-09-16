import subprocess
from enum import Enum
from pathlib import Path


class Paths(Enum):
    ROOT = Path(__file__).parents[1]
    DOCS = ROOT.joinpath("docs")
    SPHINX = DOCS.joinpath("sphinx")
    OUTPUT = SPHINX.joinpath("_build", "markdown")
    FINAL_DOC = DOCS.joinpath("docs.md")


def build_docs() -> bool:
    print("Génération de la documentation...")
    result = subprocess.run(
        ["sphinx-build", "-b", "markdown", ".", "_build/markdown"],
        cwd=Paths.SPHINX.value,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Erreur lors de la génération de la documentation:")
        print(result.stderr)
        return False

    print("Création du fichier docs.md final...")
    with open(Paths.FINAL_DOC.value, "w", encoding="utf-8") as outfile:
        # Traiter d'abord le fichier index.md s'il existe
        index_file = Paths.OUTPUT.value / "index.md"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as infile:
                content = infile.read()
                outfile.write(f"\n\n# index\n\n{content}")

        # Puis traiter tous les autres fichiers (sauf index.md)
        for md_file in sorted(Paths.OUTPUT.value.glob("*.md")):
            if md_file.name != "index.md":
                outfile.write(f"\n\n# {md_file.stem}\n\n")
                with open(md_file, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)

    print(f"Documentation générée avec succès: {Paths.FINAL_DOC.value}")
    return True


if __name__ == "__main__":
    build_docs()
