import chromadb
import sys
import json

sys.path.append(".")
sys.path.append("parsers")
from parsers.monster_parser import MonsterParser

client = chromadb.Client()
# print(chromadb.__version__)
# print(client)

collection = client.create_collection(name="monsters")
# print(collection)

with open("../../5etools-v2.28.0/data/bestiary/bestiary-mm.json") as f:
    bestiary = json.load(f)


parser = MonsterParser()
metadata, document, _ = parser.parse(bestiary["monster"][0])
print(metadata)
print(document)

id_aarakocra = f"{metadata.get('entity_type')}_{metadata.get('name').lower()}_{metadata.get('source').lower()}"

collection.add(
    ids=[id_aarakocra],
    documents=[document],
    metadatas=[metadata]
)
print("Ingéré :", id_aarakocra)

resultats = collection.query(
    query_texts=["flying creature that can summon elementals"],
    n_results=1
)
print(resultats)