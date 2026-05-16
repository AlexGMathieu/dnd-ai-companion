
"""
Script d'ingestion principale — appelle ingest_all pour chaque type d'entité 5etools
et alimente les collections ChromaDB (trinité MM/PHB/DMG 2014).
"""

import chromadb
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.monster_parser import MonsterParser
from parsers.spell_parser import SpellParser
from parsers.item_parser import ItemParser
from parsers.rule_parser import RuleParser
from parsers.trap_parser import TrapParser
from parsers.table_parser import TableParser
from parsers.background_parser import BackgroundParser
from parsers.feat_parser import FeatParser
from parsers.race_parser import RaceParser
from db.ingestion import ingest_all, get_or_create_collection

client = chromadb.PersistentClient(path=str(Path(__file__).parent.parent / "chroma"))

dico = {
    "monster-mm": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\bestiary\bestiary-mm.json",
        "parser_class": MonsterParser,
        "clef": "monster",
        "name": "monster_mm_collection"
    },
        "monster-phb": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\bestiary\bestiary-phb.json",
        "parser_class": MonsterParser,
        "clef": "monster",
        "name": "monster_phb_collection"
    },
        "monster-dmg": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\bestiary\bestiary-dmg.json",
        "parser_class": MonsterParser,
        "clef": "monster",
        "name": "monster_dmg_collection"
    },
    "spell_phb": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\spells\spells-phb.json",
        "parser_class": SpellParser,
        "clef": "spell",
        "name": "spell_phb_collection"
    },
    "item-phb": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\items.json",
        "parser_class": ItemParser,
        "clef": "item",
        "name": "item_phb_collection"
    },
    "variantrules": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\variantrules.json",
        "parser_class": RuleParser,
        "clef": "variantrule",
        "name": "variantrule_collection"
    },
    "trap": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\trapshazards.json",
        "parser_class": TrapParser,
        "clef": "trap",
        "name": "trap_collection"
    },
    "table": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\tables.json",
        "parser_class": TableParser,
        "clef": "table",
        "name": "table_collection"
    },
    "background": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\backgrounds.json",
        "parser_class": BackgroundParser,
        "clef": "background",
        "name": "background_collection"
    },
    "feat": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\feats.json",
        "parser_class": FeatParser,
        "clef": "feat",
        "name": "feat_collection"
    },
    "race": {
        "filepath": r"C:\GitHub\5etools-v2.28.0\data\races.json",
        "parser_class": RaceParser,
        "clef": "race",
        "name": "race_collection"
    },
}

for main_key in dico:
    filepath = dico[main_key]["filepath"]
    parser_class = dico[main_key]["parser_class"]
    clef = dico[main_key]["clef"]
    name = dico[main_key]["name"]
    ingest_all(filepath, parser_class, clef, client, name)
