import pytest
import sys
import chromadb
from pathlib import Path

sys.path.append("../db")
import ingestion

sys.path.append("../parsers")
import monster_parser

def test_build_entity_id_cas_nomminal():
    vampire = {"entity_type": "monster",
               "name": "Vampire", 
               "source": "MM"}
    
    entity_id = ingestion.build_entity_id(vampire)

    assert "monster_vampire_mm" == entity_id
    
def test_build_entity_id_sans_name():
    with pytest.raises(KeyError):
        ingestion.build_entity_id({"entity_type": "monster", "source": "MM"})

def test_build_entity_id_sans_source():
    with pytest.raises(KeyError):
        ingestion.build_entity_id({"entity_type": "monster", "name": "Vampire"})

def test_build_entity_id_sans_entity_type():
    with pytest.raises(KeyError):
        ingestion.build_entity_id({"name": "Vampire", "source": "MM"})

@pytest.fixture
def client_chroma():
    client = chromadb.EphemeralClient()  # client en mémoire, pas sur disque
    yield client

def test_create_collection(client_chroma):
    collection = ingestion.get_or_create_collection(client_chroma, "test")
    assert collection is not None

def test_get_collection(client_chroma):
    collection_1 = ingestion.get_or_create_collection(client_chroma, "test")
    collection_2 = ingestion.get_or_create_collection(client_chroma, "test")
    assert collection_1.name == collection_2.name

def test_get_or_create_collection_sans_nom(client_chroma):
    with pytest.raises(TypeError):
        ingestion.get_or_create_collection(client_chroma)

def test_get_or_create_collection_sans_cient(client_chroma):
    with pytest.raises(Exception):
        ingestion.get_or_create_collection("test")

def test_ingestor_nominal(client_chroma):
    entity_id = "monster_vampire_mm"
    metadata = {"entity_type": "monster", "name": "Vampire", "source": "MM"}
    document = "The dragon exhales acid in a 20-foot line that is 5 feet wide. Each creature in that line must make a {@dc 11} Dexterity saving throw, taking 18 ({@damage 4d8}) acid damage on a failed save, or half as much damage on a successful one."
    collection = ingestion.get_or_create_collection(client_chroma, "test")

    collection_ingestor = ingestion.ingestor(entity_id, metadata, document, collection)

    assert collection.count() == 1

def test_ingestor_sans_collection(client_chroma):
    entity_id = "monster_vampire_mm"
    metadata = {"entity_type": "monster", "name": "Vampire", "source": "MM"}
    document = "The dragon exhales acid in a 20-foot line that is 5 feet wide. Each creature in that line must make a {@dc 11} Dexterity saving throw, taking 18 ({@damage 4d8}) acid damage on a failed save, or half as much damage on a successful one."

    with pytest.raises(TypeError):
        ingestion.ingestor(entity_id, metadata, document)

def test_ingestor_sans_entity_id(client_chroma):
    metadata = {"entity_type": "monster", "name": "Vampire", "source": "MM"}
    document = "The dragon exhales acid in a 20-foot line that is 5 feet wide. Each creature in that line must make a {@dc 11} Dexterity saving throw, taking 18 ({@damage 4d8}) acid damage on a failed save, or half as much damage on a successful one."
    collection = ingestion.get_or_create_collection(client_chroma, "test")

    with pytest.raises(ValueError):
        ingestion.ingestor(None, metadata, document, collection)

def test_ingestor_sans_metadata(client_chroma):
    entity_id = "monster_vampire_mm"
    document = "The dragon exhales acid in a 20-foot line that is 5 feet wide. Each creature in that line must make a {@dc 11} Dexterity saving throw, taking 18 ({@damage 4d8}) acid damage on a failed save, or half as much damage on a successful one."
    collection = ingestion.get_or_create_collection(client_chroma, "test")

    with pytest.raises(ValueError):
        ingestion.ingestor(entity_id, None, document, collection)

def test_ingestor_sans_document(client_chroma):
    entity_id = "monster_vampire_mm"
    metadata = {"entity_type": "monster", "name": "Vampire", "source": "MM"}
    collection = ingestion.get_or_create_collection(client_chroma, "test")

    with pytest.raises(ValueError):
        ingestion.ingestor(entity_id, metadata, None, collection)

def test_ingest_all_nominal(client_chroma):
    filepath = Path(__file__).parent / "fixtures" / "bestiary_test.json"
    parser_class = monster_parser.MonsterParser
    clef = "monster"
    client = client_chroma
    name = "monster_test"
    ingestion.ingest_all(filepath, parser_class, clef, client, name)
    collection = ingestion.get_or_create_collection(client, name)

    assert collection.count() == 2

def test_ingest_all_filepath_inexistant(client_chroma):
    filepath = "./fixtures/fichier_qui_nexiste_pas.json"
    parser_class = monster_parser.MonsterParser
    clef = "monster"
    client = client_chroma
    name = "monster_test"

    with pytest.raises(FileNotFoundError):
        ingestion.ingest_all(filepath, parser_class, clef, client, name)
