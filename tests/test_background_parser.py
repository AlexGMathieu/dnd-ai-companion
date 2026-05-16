import pytest
import sys

sys.path.append("../parsers")
from background_parser import BackgroundParser

parser = BackgroundParser()

def test_background_parser():
    aberrant_heir = {
			"name": "Aberrant Heir",
			"source": "EFA",
			"page": 25,
			"edition": "one",
			"ability": [
				{
					"choose": {
						"weighted": {
							"from": [
								"str",
								"con",
								"cha"
							],
							"weights": [
								2,
								1
							]
						}
					}
				},
				{
					"choose": {
						"weighted": {
							"from": [
								"str",
								"con",
								"cha"
							],
							"weights": [
								1,
								1,
								1
							]
						}
					}
				}
			],
			"feats": [
				{
					"aberrant dragonmark|efa": True
				}
			],
			"skillProficiencies": [
				{
					"history": True,
					"intimidation": True
				}
			],
			"toolProficiencies": [
				{
					"disguise kit": True
				}
			],
			"startingEquipment": [
				{
					"a": [
						"dagger|xphb",
						"disguise kit|xphb",
						"costume|xphb",
						"traveler's clothes|xphb",
						{
							"value": 1600
						}
					],
					"b": [
						{
							"value": 5000
						}
					]
				}
			],
			"entries": [
				{
					"type": "list",
					"style": "list-hang-notitle",
					"items": [
						{
							"type": "item",
							"name": "Ability Scores:",
							"entry": "Strength, Constitution, Charisma"
						},
						{
							"type": "item",
							"name": "Feat:",
							"entry": "{@feat Aberrant Dragonmark|EFA}"
						},
						{
							"type": "item",
							"name": "Skill Proficiencies:",
							"entry": "{@skill History|XPHB} and {@skill Intimidation|XPHB}"
						},
						{
							"type": "item",
							"name": "Tool Proficiencies:",
							"entry": "{@item Disguise Kit|XPHB}"
						},
						{
							"type": "item",
							"name": "Equipment:",
							"entry": "Choose A or B: (A) {@item Dagger|XPHB}, {@item Disguise Kit|XPHB}, {@item Costume|XPHB}, {@item Traveler's Clothes|XPHB}, 16 GP; or (B) 50 GP"
						}
					]
				}
			],
			"hasFluff": True,
			"hasFluffImages": True
		}
    
    base, document, liens = parser.parse(aberrant_heir)

    assert "str" in base["ability"]
    assert "aberrant dragonmark|efa" in base["feats"]
    assert "history" in base["skill_proefficiencies"]
    assert "disguise kit" in base["tool_proefficiencies"]
    assert "Ability Scores:" in document
    assert "skill:history:xphb" in liens
