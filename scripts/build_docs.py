import subprocess
from enum import Enum, StrEnum
from pathlib import Path

# TODO: Actuellement je dois supprimer a la main le header `# index`, puis enlever un `#` dans les titres pour avoir une hierarchie correcte

ENCODING = "utf-8"


class Files(StrEnum):
    INDEX = "index.md"
    DOCS = "docs.md"


class Paths(Enum):
    DOCS = Path().joinpath("docs")
    SPHINX = DOCS.joinpath("sphinx")
    OUTPUT = SPHINX.joinpath("_build", "markdown")
    FINAL_DOC = DOCS.joinpath(Files.DOCS)


def fix_code_blocks(content: str) -> str:
    return content.replace("```pycon", "```python")


def run_sphinx_build():
    return subprocess.run(
        ["sphinx-build", "-b", "markdown", ".", "_build/markdown"],
        cwd=Paths.SPHINX.value,
        capture_output=True,
        text=True,
    )


def build_docs() -> bool:
    print("Génération de la documentation...")
    result = run_sphinx_build()

    if result.returncode != 0:
        print("Erreur lors de la génération de la documentation:")
        print(result.stderr)
        return False

    print("Création du fichier docs.md final...")
    with open(Paths.FINAL_DOC.value, "w", encoding="utf-8") as outfile:
        for md_file in sorted(Paths.OUTPUT.value.glob("*.md")):
            outfile.write(f"\n\n# {md_file.stem}\n\n")
            with open(md_file, "r", encoding="utf-8") as infile:
                outfile.write(fix_code_blocks(content=infile.read()))

    print(f"Documentation générée avec succès: {Paths.FINAL_DOC.value}")
    return True


if __name__ == "__main__":
    build_docs()
