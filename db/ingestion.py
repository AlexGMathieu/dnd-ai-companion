import json
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pathlib import Path

def get_or_create_collection(client, name: str):
    """
    Récupère ou crée une collection ChromaDB avec le modèle d'embedding standard.

    Args:
        client: Instance ChromaDB.
        name (str): Nom de la collection.

    Returns:
        Collection ChromaDB configurée avec paraphrase-multilingual-MiniLM-L12-v2 et métrique cosinus.
    """

    collection = client.get_or_create_collection(
        name=name,
        embedding_function = SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2"),
        configuration={
            "hnsw": {
                "space": "cosine",
                "ef_construction": 200
                }
            }
        )
    return collection

def ingestor(entity_id, metadata, document, collection):
    """
    Insère ou met à jour une entité dans une collection ChromaDB.

    Args:
        entity_id (str): Identifiant unique de l'entité.
        metadata (dict): Métadonnées de l'entité.
        document (str): Texte pour la recherche sémantique.
        collection: Collection ChromaDB cible.

    Raises:
        ValueError: Si metadata est None.
    """

    if metadata is None:
        raise ValueError("metadata ne peut pas être None")
    else:
        collection.upsert(
            ids=[entity_id],
            documents=[document],
            metadatas=[metadata]
        )
    
def build_entity_id(metadata):
    """
    Construit l'identifiant unique d'une entité au format type_nom_source.

    Args:
        metadata (dict): Métadonnées contenant entity_type, name et source.

    Returns:
        str: Identifiant stable (ex: monster_goblin_mm).
    """

    entity_id = f"{metadata['entity_type']}_{metadata['name'].lower()}_{metadata['source'].lower()}"
    return entity_id
    
def ingest_all(filepath, parser_class, clef, client, name):
    """
    Orchestre l'ingestion complète d'un fichier JSON 5etools dans ChromaDB.

    Args:
        filepath: Chemin vers le fichier JSON 5etools.
        parser_class: Classe parser à instancier.
        clef (str): Clé racine dans le JSON (ex: 'monster', 'spell').
        client: Instance ChromaDB.
        name (str): Nom de la collection cible.
    """
        
    collection = get_or_create_collection(client, name)
    with open(filepath) as f:
        data = json.load(f)
    parser = parser_class()
    for i in range(len(data[clef])):
        metadata, document, _ = parser.parse(data[clef][i])
        entity_id = build_entity_id(metadata)
        ingestor(entity_id, metadata, document, collection)