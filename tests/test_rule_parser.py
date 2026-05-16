import pytest
import sys

sys.path.append("../parsers")
from rule_parser import RuleParser

parser = RuleParser()



def test_rule_parser():
    rule =		{
            "name": "Action",
            "source": "XPHB",
            "page": 360,
            "srd52": True,
            "basicRules2024": True,
            "ruleType": "C",
            "entries": [
                "On your turn, you can take one action. Choose which action to take from those below or from the special actions provided by your features. These actions are defined elsewhere in this glossary:",
                {
                    "type": "list",
                    "style": "list-hang-notitle",
                    "columns": 4,
                    "items": [
                        "{@action Attack|XPHB}",
                        "{@action Dodge|XPHB}",
                        "{@action Dash|XPHB}",
                        "{@action Help|XPHB}",
                        "{@action Disengage|XPHB}",
                        "{@action Hide|XPHB}",
                        "{@action Influence|XPHB}",
                        "{@action Magic|XPHB}",
                        "{@action Ready|XPHB}",
                        "{@action Search|XPHB}",
                        "{@action Study|XPHB}",
                        "{@action Utilize|XPHB}"
                    ]
                }
            ]
        }


    base, document, liens = parser.parse(rule)

    assert len(liens) ==12
    assert "Action" == base["name"]
    assert "action:attack:xphb" in liens
    assert "On your turn, you can take one action" in document
    
def test_condition_parser():
    condition_parser = RuleParser(entity_type="condition")
    condtion = {
            "name": "Blinded",
            "source": "PHB",
            "page": 290,
            "srd": True,
            "basicRules": True,
            "otherSources": [
                {
                    "source": "RMR",
                    "page": 62
                },
                {
                    "source": "HftT",
                    "page": 48
                }
            ],
            "reprintedAs": [
                "Blinded|XPHB"
            ],
            "entries": [
                {
                    "type": "list",
                    "items": [
                        "A blinded creature can't see and automatically fails any ability check that requires sight.",
                        "Attack rolls against the creature have advantage, and the creature's attack rolls have disadvantage."
                    ]
                }
            ],
            "hasFluffImages": True
        }
    
    
    base, document, liens = condition_parser.parse(condtion)
    
    assert "Blinded" == base["name"]
    assert "condition" in document
    

def test_skill_parser():
    skill_parser = RuleParser(entity_type = "skill")
    skill = {
            "name": "Acrobatics",
            "source": "PHB",
            "page": 176,
            "srd": True,
            "basicRules": True,
            "reprintedAs": [
                "Acrobatics|XPHB"
            ],
            "ability": "dex",
            "entries": [
                "Your Dexterity (Acrobatics) check covers your attempt to stay on your feet in a tricky situation, such as when you're trying to run across a sheet of ice, balance on a tightrope, or stay upright on a rocking ship's deck. The DM might also call for a Dexterity (Acrobatics) check to see if you can perform acrobatic stunts, including dives, rolls, somersaults, and flips."
            ]
        }
    
    base, document, liens = skill_parser.parse(skill)
    
    assert "dex" == base["ability"]
    assert "dex" in document

def test_optional_feature_parser():
    feature_parser = RuleParser(entity_type = "optionalfeature")
    feature = {
			"name": "Agonizing Blast",
			"source": "PHB",
			"page": 110,
			"srd": True,
			"reprintedAs": [
				"Agonizing Blast|XPHB"
			],
			"featureType": [
				"EI"
			],
			"prerequisite": [
				{
					"spell": [
						"eldritch blast#c"
					]
				}
			],
			"entries": [
				"When you cast {@spell eldritch blast}, add your Charisma modifier to the damage it deals on a hit."
			]
		}
    
    base, document, liens = feature_parser.parse(feature)

    assert "Eldritch Invocation" in document
    assert "spell:eldritch blast:phb" in liens