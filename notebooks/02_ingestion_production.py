import chromadb
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.monster_parser import MonsterParser
from db.ingestion import ingest_all, get_or_create_collection

client = chromadb.PersistentClient(path=str(Path(__file__).parent.parent / "chroma"))

filepath = Path(__file__).parent.parent.parent.parent / "5etools-v2.28.0/data/bestiary/bestiary-mm.json"
parser = MonsterParser
clef = "monster"
name = "monsters"

client.delete_collection(name)
ingest_all(filepath, parser, clef, client, name)
collection = get_or_create_collection(client, name)

resultats = collection.query(
    query_texts=["creature that petrifies with constitution saving throw"],
    n_results=1
)
print(resultats)