"""
test_model.py
-------------
Modèle Pydantic pour les questions de test RAG D&D.

Inspiré de : Ed Donner — LLM Engineering, Week 5, evaluation/test.py
Adapté pour : DnD AI Companion — Session 18
"""

import json
from pathlib import Path
from pydantic import BaseModel, Field

# Chemin par défaut (peut être surchargé dans les appels)
DEFAULT_TEST_FILE = Path(__file__).parent / "tests.jsonl"


class TestQuestion(BaseModel):
    """Une question de test avec keywords et réponse de référence."""

    question: str = Field(description="La question posée au système RAG")
    keywords: list[str] = Field(
        description="Mots-clés devant apparaître textuellement dans le contexte récupéré"
    )
    reference_answer: str = Field(description="La réponse de référence attendue")
    category: str = Field(
        description=(
            "Catégorie de la question : "
            "direct_fact | temporal | numerical | comparative | "
            "relationship | spanning | holistic"
        )
    )


def load_tests(filepath: Path | str | None = None) -> list[TestQuestion]:
    """
    Charge les questions de test depuis un fichier JSONL.

    Args:
        filepath: Chemin vers le fichier JSONL. Utilise DEFAULT_TEST_FILE si None.

    Returns:
        Liste de TestQuestion validés par Pydantic.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si une ligne JSONL est invalide.
    """
    path = Path(filepath) if filepath else DEFAULT_TEST_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier de tests introuvable : {path}\n"
            "Génère-le d'abord avec : uv run evaluation/generate_golden_dataset.py"
        )

    tests = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                tests.append(TestQuestion(**data))
            except (json.JSONDecodeError, Exception) as e:
                raise ValueError(f"Ligne {line_num} invalide dans {path}: {e}")

    return tests


def load_tests_by_category(category: str, filepath: Path | str | None = None) -> list[TestQuestion]:
    """
    Charge uniquement les questions d'une catégorie donnée.

    Args:
        category: Nom de la catégorie (ex: 'direct_fact', 'spanning').
        filepath: Chemin vers le fichier JSONL.

    Returns:
        Liste filtrée de TestQuestion.
    """
    all_tests = load_tests(filepath)
    return [t for t in all_tests if t.category == category]


def summary(filepath: Path | str | None = None) -> None:
    """Affiche un résumé du dataset de test."""
    from collections import Counter
    tests = load_tests(filepath)
    counts = Counter(t.category for t in tests)
    print(f"Total : {len(tests)} questions")
    print("Répartition par catégorie :")
    for cat, count in sorted(counts.items()):
        print(f"  - {cat}: {count}")


if __name__ == "__main__":
    summary()
