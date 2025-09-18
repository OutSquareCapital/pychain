import subprocess
from enum import Enum, StrEnum
from pathlib import Path

# TODO: Actuellement je dois supprimer a la main le header `# index`, puis enlever un `#` dans les titres pour avoir une hierarchie correcte
# TODO: fix le probleme des docs qui ne couvrent pas les methodes namespace

ENCODING = "utf-8"


class Files(StrEnum):
    INDEX = "index.md"
    DOCS = "docs.md"


class Paths(Enum):
    DOCS = Path().joinpath("docs")
    SPHINX = DOCS.joinpath("sphinx")
    OUTPUT = SPHINX.joinpath("_build", "markdown")
    FINAL_DOC = DOCS.joinpath(Files.DOCS)


def run_sphinx_build():
    return subprocess.run(
        ["sphinx-build", "-b", "markdown", ".", "_build/markdown"],
        cwd=Paths.SPHINX.value,
        capture_output=True,
        text=True,
    )


def sorted_md_files() -> list[Path]:
    return sorted(Paths.OUTPUT.value.glob("*.md"))


def build_docs() -> bool:
    print("Génération de la documentation...")
    result = run_sphinx_build()

    if result.returncode != 0:
        print("Erreur lors de la génération de la documentation:")
        print(result.stderr)
        return False

    print("Création du fichier docs.md final...")
    with open(Paths.FINAL_DOC.value, "w", encoding="utf-8") as outfile:
        for md_file in sorted_md_files():
            outfile.write(f"\n\n# {md_file.stem}\n\n")
            with open(md_file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read().replace("```pycon", "```python"))

    print(f"Documentation générée avec succès: {Paths.FINAL_DOC.value}")
    return True


if __name__ == "__main__":
    build_docs()
