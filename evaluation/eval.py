"""
eval.py
-------
Évaluation RAG du DnD AI Companion.
Métriques : MRR, nDCG, keyword coverage (Phase 1 — sans LLM judge).

Usage CLI :
    uv run evaluation/eval.py                  → évalue tout le dataset
    uv run evaluation/eval.py --category spanning  → filtre par catégorie
    uv run evaluation/eval.py --n 10           → évalue les 10 premières questions

Inspiré de : Ed Donner — LLM Engineering, Week 5, evaluation/eval.py
Adapté pour : DnD AI Companion — ChromaDB + paraphrase-multilingual-MiniLM-L12-v2
"""

import argparse
import math
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pydantic import BaseModel, Field

# Ajout du dossier parent au path pour les imports relatifs
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.test_model import TestQuestion, load_tests, load_tests_by_category

# ---------------------------------------------------------------------------
# Configuration ChromaDB
# ---------------------------------------------------------------------------
CHROMA_PATH = Path(__file__).parent.parent / "chroma"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 10  # Nombre de documents récupérés par requête

# Collections à interroger (toutes les collections ingérées Phase 1)
COLLECTIONS = [
    "monster_mm_collection",
    "monster_phb_collection",
    "monster_dmg_collection",
    "spell_phb_collection",
    "item_phb_collection",
    "variantrule_collection",
    "trap_collection",
    "table_collection",
    "background_collection",
    "feat_collection",
    "race_collection",
]


# ---------------------------------------------------------------------------
# Modèles Pydantic
# ---------------------------------------------------------------------------

class RetrievalEval(BaseModel):
    """Métriques d'évaluation de la retrieval pour une question."""

    question: str
    category: str
    mrr: float = Field(description="Mean Reciprocal Rank — moyenne sur tous les keywords")
    ndcg: float = Field(description="Normalized Discounted Cumulative Gain (pertinence binaire)")
    keywords_found: int = Field(description="Nombre de keywords trouvés dans le top-k")
    total_keywords: int = Field(description="Nombre total de keywords à trouver")
    keyword_coverage: float = Field(description="Pourcentage de keywords trouvés (0-100)")


class EvalSummary(BaseModel):
    """Résumé global de l'évaluation."""

    total_questions: int
    avg_mrr: float
    avg_ndcg: float
    avg_keyword_coverage: float
    results_by_category: dict[str, dict]  # catégorie → {avg_mrr, avg_ndcg, avg_coverage, count}


# ---------------------------------------------------------------------------
# Client ChromaDB (singleton)
# ---------------------------------------------------------------------------

_client = None
_embedding_fn = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def get_embedding_fn() -> SentenceTransformerEmbeddingFunction:
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _embedding_fn


# ---------------------------------------------------------------------------
# Retrieval : interroge toutes les collections, fusionne les résultats
# ---------------------------------------------------------------------------

def fetch_context(question: str, k: int = TOP_K) -> list[str]:
    """
    Interroge toutes les collections ChromaDB et retourne les k documents
    les plus proches, triés par distance cosinus.

    Args:
        question: La question posée au système RAG.
        k: Nombre de documents à récupérer par collection.

    Returns:
        Liste de strings (documents), triée par distance (plus proche en premier).
    """
    client = get_chroma_client()
    embedding_fn = get_embedding_fn()

    all_results = []  # liste de (distance, document_text)

    for collection_name in COLLECTIONS:
        try:
            collection = client.get_collection(
                name=collection_name,
                embedding_function=embedding_fn,
            )
            results = collection.query(
                query_texts=[question],
                n_results=min(k, collection.count()),
                include=["documents", "distances"],
            )
            docs = results["documents"][0]
            distances = results["distances"][0]
            for doc, dist in zip(docs, distances):
                all_results.append((dist, doc))
        except Exception:
            # Collection absente ou vide : on skip silencieusement
            continue

    # Tri par distance croissante (cosinus : plus petit = plus proche)
    all_results.sort(key=lambda x: x[0])

    # Retourner les k meilleurs documents (texte seulement)
    return [doc for _, doc in all_results[:k]]


# ---------------------------------------------------------------------------
# Métriques : MRR, nDCG, keyword coverage
# ---------------------------------------------------------------------------

def calculate_mrr(keyword: str, retrieved_docs: list[str]) -> float:
    """
    Calcule le Reciprocal Rank pour un keyword donné.

    Le keyword est recherché (case-insensitive) dans chaque document récupéré.
    Si trouvé au rang r, RR = 1/r. Sinon RR = 0.

    Args:
        keyword: Le mot-clé à chercher.
        retrieved_docs: Liste ordonnée de documents récupérés.

    Returns:
        Reciprocal Rank (float entre 0 et 1).
    """
    keyword_lower = keyword.lower()
    for rank, doc in enumerate(retrieved_docs, start=1):
        if keyword_lower in doc.lower():
            return 1.0 / rank
    return 0.0


def calculate_dcg(relevances: list[int], k: int) -> float:
    """
    Calcule le Discounted Cumulative Gain.

    Args:
        relevances: Liste de pertinences binaires (0 ou 1) par rang.
        k: Nombre maximum de rangs à considérer.

    Returns:
        DCG (float).
    """
    dcg = 0.0
    for i in range(min(k, len(relevances))):
        dcg += relevances[i] / math.log2(i + 2)  # rang commence à 1 → log2(rang+1)
    return dcg


def calculate_ndcg(keyword: str, retrieved_docs: list[str], k: int = TOP_K) -> float:
    """
    Calcule le Normalized Discounted Cumulative Gain pour un keyword.

    Pertinence binaire : 1 si le keyword apparaît dans le document, 0 sinon.
    IDCG = DCG optimal = keyword trouvé au rang 1.

    Args:
        keyword: Le mot-clé à chercher.
        retrieved_docs: Liste ordonnée de documents récupérés.
        k: Nombre de rangs à considérer.

    Returns:
        nDCG (float entre 0 et 1).
    """
    keyword_lower = keyword.lower()
    relevances = [
        1 if keyword_lower in doc.lower() else 0
        for doc in retrieved_docs[:k]
    ]
    dcg = calculate_dcg(relevances, k)

    # IDCG : meilleur cas possible = keyword au rang 1
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = calculate_dcg(ideal_relevances, k)

    return dcg / idcg if idcg > 0 else 0.0


# ---------------------------------------------------------------------------
# Évaluation d'une question
# ---------------------------------------------------------------------------

def evaluate_retrieval(test: TestQuestion, k: int = TOP_K) -> RetrievalEval:
    """
    Évalue la qualité de la retrieval pour une question de test.

    Args:
        test: La question de test avec ses keywords.
        k: Nombre de documents récupérés.

    Returns:
        RetrievalEval avec MRR, nDCG, et keyword coverage.
    """
    retrieved_docs = fetch_context(test.question, k=k)

    # MRR : moyenne sur tous les keywords
    mrr_scores = [calculate_mrr(kw, retrieved_docs) for kw in test.keywords]
    avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0

    # nDCG : moyenne sur tous les keywords
    ndcg_scores = [calculate_ndcg(kw, retrieved_docs, k) for kw in test.keywords]
    avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0

    # Keyword coverage
    keywords_found = sum(1 for s in mrr_scores if s > 0)
    total_keywords = len(test.keywords)
    keyword_coverage = (keywords_found / total_keywords * 100) if total_keywords > 0 else 0.0

    return RetrievalEval(
        question=test.question,
        category=test.category,
        mrr=avg_mrr,
        ndcg=avg_ndcg,
        keywords_found=keywords_found,
        total_keywords=total_keywords,
        keyword_coverage=keyword_coverage,
    )


# ---------------------------------------------------------------------------
# Évaluation globale
# ---------------------------------------------------------------------------

def evaluate_all(
    tests: list[TestQuestion],
    verbose: bool = False,
) -> EvalSummary:
    """
    Évalue toutes les questions et retourne un résumé global.

    Args:
        tests: Liste de TestQuestion.
        verbose: Affiche chaque résultat si True.

    Returns:
        EvalSummary avec métriques globales et par catégorie.
    """
    results: list[RetrievalEval] = []

    for i, test in enumerate(tests):
        result = evaluate_retrieval(test)
        results.append(result)

        if verbose:
            print(
                f"[{i+1:3d}/{len(tests)}] {test.category:15s} | "
                f"MRR={result.mrr:.3f} | nDCG={result.ndcg:.3f} | "
                f"Coverage={result.keyword_coverage:.0f}% | "
                f"{test.question[:60]}"
            )
        else:
            # Barre de progression simple
            print(f"\r  Progression : {i+1}/{len(tests)}", end="", flush=True)

    if not verbose:
        print()  # saut de ligne après la barre de progression

    # Métriques globales
    avg_mrr = sum(r.mrr for r in results) / len(results)
    avg_ndcg = sum(r.ndcg for r in results) / len(results)
    avg_coverage = sum(r.keyword_coverage for r in results) / len(results)

    # Métriques par catégorie
    from collections import defaultdict
    cat_data: dict[str, list[RetrievalEval]] = defaultdict(list)
    for r in results:
        cat_data[r.category].append(r)

    results_by_category = {}
    for cat, cat_results in sorted(cat_data.items()):
        results_by_category[cat] = {
            "count": len(cat_results),
            "avg_mrr": sum(r.mrr for r in cat_results) / len(cat_results),
            "avg_ndcg": sum(r.ndcg for r in cat_results) / len(cat_results),
            "avg_coverage": sum(r.keyword_coverage for r in cat_results) / len(cat_results),
        }

    return EvalSummary(
        total_questions=len(results),
        avg_mrr=avg_mrr,
        avg_ndcg=avg_ndcg,
        avg_keyword_coverage=avg_coverage,
        results_by_category=results_by_category,
    )


def print_summary(summary: EvalSummary) -> None:
    """Affiche le résumé de l'évaluation dans la console."""
    print("\n" + "=" * 60)
    print("RÉSULTATS ÉVALUATION RAG — DnD AI Companion")
    print("=" * 60)
    print(f"Total questions évaluées : {summary.total_questions}")
    print(f"\nMétriques globales :")
    print(f"  MRR               : {summary.avg_mrr:.4f}")
    print(f"  nDCG              : {summary.avg_ndcg:.4f}")
    print(f"  Keyword Coverage  : {summary.avg_keyword_coverage:.1f}%")
    print(f"\nPar catégorie :")
    for cat, metrics in summary.results_by_category.items():
        print(
            f"  {cat:20s} | n={metrics['count']:3d} | "
            f"MRR={metrics['avg_mrr']:.3f} | "
            f"nDCG={metrics['avg_ndcg']:.3f} | "
            f"Coverage={metrics['avg_coverage']:.0f}%"
        )
    print("=" * 60)


# ---------------------------------------------------------------------------
# Point d'entrée CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Évaluation RAG — DnD AI Companion"
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filtrer par catégorie (ex: direct_fact, spanning...)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="Limiter le nombre de questions évaluées",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Afficher chaque résultat individuel",
    )
    parser.add_argument(
        "--tests-file",
        type=str,
        default=None,
        help="Chemin vers le fichier tests.jsonl (défaut : evaluation/tests.jsonl)",
    )
    args = parser.parse_args()

    # Chargement des tests
    if args.category:
        tests = load_tests_by_category(args.category, args.tests_file)
        print(f"Catégorie '{args.category}' : {len(tests)} questions chargées")
    else:
        tests = load_tests(args.tests_file)
        print(f"{len(tests)} questions chargées")

    if args.n:
        tests = tests[: args.n]
        print(f"Limité à {len(tests)} questions")

    if not tests:
        print("Aucune question à évaluer.")
        sys.exit(1)

    # Évaluation
    print(f"\nLancement de l'évaluation (TOP_K={TOP_K})...")
    summary = evaluate_all(tests, verbose=args.verbose)
    print_summary(summary)


if __name__ == "__main__":
    main()
