import pytest
import sys

sys.path.append("../parsers")
from class_parser import ClassParser

parser = ClassParser()

def test_class_parser():
    flash_of_genius = {
                "name": "Flash of Genius",
                "source": "EFA",
                "page": 10,
                "className": "Artificer",
                "classSource": "EFA",
                "level": 7,
                "entries": [
                    "When you or a creature you can see within 30 feet of you fails an ability check or a saving throw, you can take a {@variantrule Reaction|XPHB} to add a bonus to the roll, potentially causing it to succeed. The bonus equals your Intelligence modifier (minimum of +1).",
                    "You can take this {@variantrule Reaction|XPHB} a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a {@variantrule Long Rest|XPHB}."
                ]
            }
    
    base, document, liens = parser.parse(flash_of_genius)

    assert "Artificer" in base["className"]
    assert 7 == base["level"]
    assert "EFA" in base["source"]
    assert "When you or a creature you can see within 30 feet" in document
    assert "rule:reaction:xphb" in liens


