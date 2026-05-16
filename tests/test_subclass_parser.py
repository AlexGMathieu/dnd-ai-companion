import pytest
import sys

sys.path.append("../parsers")
from subclass_parser import SubclassParser

parser = SubclassParser()

def test_subclass_parser():
    alchemical_savant = 		{
			"name": "Alchemical Savant",
			"source": "EFA",
			"page": 14,
			"className": "Artificer",
			"classSource": "EFA",
			"subclassShortName": "Alchemist",
			"subclassSource": "EFA",
			"level": 5,
			"header": 2,
			"entries": [
				"Whenever you cast a spell using your {@item Alchemist's Supplies|XPHB} as the {@variantrule Spellcasting Focus|XPHB}, you gain a bonus to one roll of the spell. That roll must restore {@variantrule Hit Points|XPHB} or be a damage roll that deals Acid, Fire, or Poison damage. The bonus equals your Intelligence modifier (minimum bonus of +1)."
			]
		}
    
    base, document, liens = parser.parse(alchemical_savant)

    assert "Artificer" in base["className"]
    assert "Alchemist" in base["subclassShortName"]
    assert 5 == base["level"]
    assert "EFA" in base["subclassSource"]
    assert "Whenever you cast a spell using your" in document
    assert "item:alchemist's supplies:xphb" in liens


