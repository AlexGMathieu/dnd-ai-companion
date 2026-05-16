"""
generate_golden_dataset.py
--------------------------
Génère un golden dataset D&D pour l'évaluation RAG du DnD AI Companion.

Usage :
    uv run evaluation/generate_golden_dataset.py

Sortie :
    evaluation/tests.jsonl  (150 questions réparties en 7 catégories)

Dépendances :
    anthropic, uv

Inspiré de : Ed Donner — LLM Engineering, Week 5
Adapté pour : DnD AI Companion — Session 18
"""

import json
import random
import sys
from dotenv import load_dotenv
from pathlib import Path

import anthropic

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
DATA_DIR = Path(r"C:\GitHub\5etools-v2.28.0\data")
OUTPUT_FILE = Path(__file__).parent / "tests.jsonl"

# ---------------------------------------------------------------------------
# Catégories de questions (7 types, ~20-25 questions chacune)
# ---------------------------------------------------------------------------
CATEGORIES = [
    "direct_fact",    # Faits factuels directs  : nom, CR, type, école de magie...
    "temporal",       # Contexte temporel / niveau : sorts de niveau X, monstres CR Y
    "numerical",      # Chiffres : HP, dégâts, portée, durée...
    "comparative",    # Comparaison : quel sort fait le plus de dégâts ? qui est le plus rapide ?
    "relationship",   # Relations : quels sorts un paladin peut-il lancer ?
    "spanning",       # Multi-entités : monstre + sort + objet dans la même réponse
    "holistic",       # Vue d'ensemble : combien de sorts de niveau 9 ? types de monstres...
]

QUESTIONS_PER_CATEGORY = 22  # ~154 total, on garde 150

# ---------------------------------------------------------------------------
# Échantillonnage des données sources
# ---------------------------------------------------------------------------

def load_sample(filepath: Path, key: str, n: int = 30) -> list[dict]:
    """Charge un échantillon aléatoire d'entités depuis un fichier JSON 5etools."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    entities = data.get(key, [])
    return random.sample(entities, min(n, len(entities)))


def collect_source_data() -> dict:
    """Collecte un échantillon représentatif de toutes les collections ingérées."""
    return {
        "monsters_mm": load_sample(DATA_DIR / "bestiary" / "bestiary-mm.json", "monster", 40),
        "monsters_phb": load_sample(DATA_DIR / "bestiary" / "bestiary-phb.json", "monster", 10),
        "monsters_dmg": load_sample(DATA_DIR / "bestiary" / "bestiary-dmg.json", "monster", 10),
        "spells": load_sample(DATA_DIR / "spells" / "spells-phb.json", "spell", 40),
        "items": load_sample(DATA_DIR / "items.json", "item", 30),
        "backgrounds": load_sample(DATA_DIR / "backgrounds.json", "background", 15),
        "feats": load_sample(DATA_DIR / "feats.json", "feat", 15),
        "races": load_sample(DATA_DIR / "races.json", "race", 15),
    }


def serialize_sample(data: dict) -> str:
    """Sérialise l'échantillon en texte compact pour le prompt Claude."""
    lines = []
    for category, entities in data.items():
        lines.append(f"\n=== {category.upper()} ===")
        for e in entities[:15]:  # max 15 par catégorie dans le prompt
            # Champs clés seulement pour limiter les tokens
            summary = {
                k: v for k, v in e.items()
                if k in ("name", "source", "cr", "type", "level", "school",
                         "range", "duration", "time", "rarity", "value",
                         "skillProficiencies", "speed", "size", "entries")
                and v is not None
            }
            # Tronquer entries pour éviter l'explosion de tokens
            if "entries" in summary:
                summary["entries"] = str(summary["entries"])[:200] + "..."
            lines.append(json.dumps(summary, ensure_ascii=False))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Prompt de génération
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Tu es un expert D&D 5e et un ingénieur en évaluation RAG.
Tu génères des questions de test pour évaluer un système RAG sur les données D&D 5e (5etools).

Règles strictes :
1. Chaque question doit être précise, factuelle, et avoir une réponse vérifiable dans les données fournies.
2. Les keywords doivent être des mots/expressions qui APPARAISSENT textuellement dans le document ChromaDB correspondant.
3. La reference_answer doit être courte (1-2 phrases max) et factuelle.
4. Utilise UNIQUEMENT des entités présentes dans les données fournies — jamais d'entités inventées.
5. Varie les collections interrogées (monstres, sorts, objets, backgrounds, feats, races).
6. Retourne UNIQUEMENT du JSON valide, sans markdown, sans commentaires.

Format de sortie (tableau JSON) :
[
  {
    "question": "...",
    "keywords": ["mot1", "mot2", "mot3"],
    "reference_answer": "...",
    "category": "direct_fact"
  }
]"""


def build_user_prompt(category: str, n: int, source_data_text: str) -> str:
    """Construit le prompt utilisateur pour une catégorie donnée."""

    category_instructions = {
        "direct_fact": (
            f"Génère {n} questions sur des faits directs D&D 5e. "
            "Ex: 'Quel est le CR du Goblin ?', 'Quelle est l'école du sort Fireball ?', "
            "'Quelle est la rareté de l'épée +1 ?'. "
            "Les keywords doivent inclure le nom de l'entité et la valeur de la réponse."
        ),
        "temporal": (
            f"Génère {n} questions sur des informations contextuelles de niveau/durée/temps. "
            "Ex: 'Quelle est la durée de concentration du sort Fly ?', "
            "'Quel est le temps d'incantation de Fireball ?', "
            "'À quel niveau se lance le sort Wish ?'. "
        ),
        "numerical": (
            f"Génère {n} questions sur des valeurs numériques D&D. "
            "Ex: 'Quelle est la portée du sort Magic Missile ?', "
            "'Combien de Hit Points a le Goblin ?', "
            "'Quelle est la valeur en PO de l'objet X ?'. "
        ),
        "comparative": (
            f"Génère {n} questions qui impliquent une comparaison ou une caractéristique distinctive. "
            "Ex: 'Quel est le background qui donne les compétences History et Religion ?', "
            "'Quel sort de niveau 1 a une portée de 120 feet ?'. "
        ),
        "relationship": (
            f"Génère {n} questions sur des relations entre entités D&D. "
            "Ex: 'Quelles compétences le background Acolyte procure-t-il ?', "
            "'Quel type de créature est l'Aboleth ?', "
            "'Quels outils maîtrise le background Criminal ?'. "
        ),
        "spanning": (
            f"Génère {n} questions qui nécessitent de croiser deux informations sur la même entité. "
            "Ex: 'Quel est le CR du monstre de type Dragon le plus courant dans le MM ?', "
            "'Quel background PHB donne à la fois History et Insight ?'. "
        ),
        "holistic": (
            f"Génère {n} questions de vue d'ensemble sur les collections. "
            "Ex: 'Quels sont les backgrounds qui donnent la compétence Stealth ?', "
            "'Combien de sorts de niveau 9 existent dans le PHB ?'. "
            "Ces questions peuvent nécessiter de parcourir plusieurs entités."
        ),
    }

    return f"""Catégorie : {category}
Instructions : {category_instructions[category]}

Données D&D 5e disponibles (extrait) :
{source_data_text}

Génère exactement {n} questions de catégorie '{category}' basées UNIQUEMENT sur les données ci-dessus.
Retourne un tableau JSON valide de {n} objets, sans aucun texte avant ou après."""


# ---------------------------------------------------------------------------
# Appel API et parsing
# ---------------------------------------------------------------------------

def generate_questions_for_category(
    client: anthropic.Anthropic,
    category: str,
    n: int,
    source_data_text: str,
) -> list[dict]:
    """Appelle Claude pour générer n questions d'une catégorie donnée."""
    print(f"  Génération catégorie '{category}' ({n} questions)...", end=" ", flush=True)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(category, n, source_data_text),
            }
        ],
    )

    raw = response.content[0].text.strip()

    # Nettoyage defensif : supprimer backticks markdown si présents
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    try:
        questions = json.loads(raw)
        # Validation minimale : liste de dicts avec les champs requis
        valid = []
        for q in questions:
            if all(k in q for k in ("question", "keywords", "reference_answer", "category")):
                q["category"] = category  # forcer la catégorie correcte
                valid.append(q)
        print(f"✅ {len(valid)}/{n} valides")
        return valid
    except json.JSONDecodeError as e:
        print(f"❌ JSON invalide : {e}")
        print(f"   Raw (100 chars) : {raw[:100]}")
        return []


# ---------------------------------------------------------------------------
# Point d'entrée principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("DnD AI Companion — Génération Golden Dataset")
    print("=" * 60)

    # Initialisation client Anthropic
    client = anthropic.Anthropic()  # utilise ANTHROPIC_API_KEY

    # Collecte des données sources
    print("\n[1/3] Chargement des données 5etools...")
    source_data = collect_source_data()
    source_data_text = serialize_sample(source_data)
    print(f"  {sum(len(v) for v in source_data.values())} entités chargées")
    print(f"  Texte prompt : {len(source_data_text)} caractères")

    # Génération par catégorie
    print("\n[2/3] Génération des questions via Claude API...")
    all_questions = []
    for category in CATEGORIES:
        questions = generate_questions_for_category(
            client, category, QUESTIONS_PER_CATEGORY, source_data_text
        )
        all_questions.extend(questions)

    print(f"\n  Total généré : {len(all_questions)} questions")

    # Troncature à 150 si nécessaire, shuffle pour mélanger les catégories
    random.shuffle(all_questions)
    all_questions = all_questions[:150]

    # Écriture JSONL
    print("\n[3/3] Écriture du fichier tests.jsonl...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for q in all_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Récapitulatif par catégorie
    print(f"\n✅ Golden dataset écrit : {OUTPUT_FILE}")
    print(f"   Total questions : {len(all_questions)}")
    print("\n   Répartition par catégorie :")
    from collections import Counter
    counts = Counter(q["category"] for q in all_questions)
    for cat, count in sorted(counts.items()):
        print(f"   - {cat}: {count}")


if __name__ == "__main__":
    main()
