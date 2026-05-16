import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pathlib import Path

CHROMA_PATH = Path(__file__).parent.parent / "chroma"
COLLECTION_NAME = "monster_mm_collection"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL),
    )
    return collection

def fetch_results(query: str, k: int = TOP_K):
    collection = get_collection()
    all_results = []

    results = collection.query(
        query_texts=[query],
        n_results=min(k, collection.count()),
        include=["metadatas", "documents", "distances"],
    )
    docs = results["documents"][0]
    distances = results["distances"][0]
    metadata = results["metadatas"][0]
    for doc, dist, meta in zip(docs, distances, metadata):
        all_results.append((meta, doc, dist))
    return all_results[:k]


# --- UI ---
st.title("🐉 DnD AI Companion")

query = st.text_input("Rechercher un monstre...")

if st.button("Rechercher") and query:
    results = fetch_results(query)
    for metadata, document, distance in results:
        with st.expander(f"{metadata['name']} (CR {metadata['cr']}) — distance: {distance:.3f}"):
            st.markdown(f"**Type** : {metadata['entity_type']}")
            st.markdown(f"**Size** : {metadata['size']}")
            st.markdown(f"**Source** : {metadata['source']}")
            st.markdown("---")
            st.markdown(document)

