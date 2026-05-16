import pytest
import sys

sys.path.append("../parsers")
from race_parser import RaceParser

parser = RaceParser()

def test_race_parser_fly():
    aaracokra = 		{
			"name": "Aarakocra",
			"source": "MPMM",
			"page": 5,
			"lineage": "VRGR",
			"size": [
				"M"
			],
			"speed": {
				"walk": 30,
				"fly": True
			},
			"traitTags": [
				"Natural Weapon"
			],
			"soundClip": {
				"type": "internal",
				"path": "races/aarakocra.opus"
			},
			"additionalSpells": [
				{
					"innate": {
						"3": [
							"gust of wind"
						]
					},
					"ability": {
						"choose": [
							"int",
							"wis",
							"cha"
						]
					}
				}
			],
			"entries": [
				{
					"type": "entries",
					"name": "Flight",
					"entries": [
						"Because of your wings, you have a flying speed equal to your walking speed. You can't use this flying speed if you're wearing medium or heavy armor."
					]
				},
				{
					"type": "entries",
					"name": "Talons",
					"entries": [
						"You have talons that you can use to make unarmed strikes. When you hit with them, the strike deals {@damage 1d6} + your Strength modifier slashing damage, instead of the bludgeoning damage normal for an unarmed strike."
					]
				},
				{
					"type": "entries",
					"name": "Wind Caller",
					"entries": [
						"Starting at 3rd level, you can cast the {@spell gust of wind} spell with this trait, without requiring a material component. Once you cast the spell with this trait, you can't do so again until you finish a long rest. You can also cast the spell using any spell slots you have of 2nd level or higher.",
						"Intelligence, Wisdom, or Charisma is your spellcasting ability for when you cast {@spell gust of wind} with this trait (choose when you select this race)."
					]
				}
			],
			"hasFluff": True,
			"hasFluffImages": True
		}
    
    base, document, liens = parser.parse(aaracokra)

    assert "fly" in base["speed"]
    assert "spell:gust of wind:phb" in liens
    assert "Natural Weapon" in base["traitTags"]
    assert "Natural Weapon" in document
    assert "You have talons that you can use to make unarmed strikes." in document

def test_race_parser_simple():
    aasimar = {
			"name": "Aasimar",
			"source": "DMG",
			"page": 286,
			"reprintedAs": [
				"Aasimar|XPHB"
			],
			"size": [
				"M"
			],
			"speed": 30,
			"ability": [
				{
					"wis": 1,
					"cha": 2
				}
			],
			"age": {
				"mature": 20,
				"max": 100
			},
			"darkvision": 60,
			"languageProficiencies": [
				{
					"common": True,
					"celestial": True
				}
			],
			"resist": [
				"necrotic",
				"radiant"
			],
			"soundClip": {
				"type": "internal",
				"path": "races/aasimar.opus"
			},
			"additionalSpells": [
				{
					"innate": {
						"3": {
							"daily": {
								"1": [
									"lesser restoration"
								]
							}
						},
						"5": {
							"daily": {
								"1": [
									"daylight"
								]
							}
						}
					},
					"ability": "cha",
					"known": {
						"1": [
							"light#c"
						]
					}
				}
			],
			"entries": [
				{
					"name": "Age",
					"type": "entries",
					"entries": [
						"Aasimar mature at the same rate as humans but live a few years longer."
					]
				},
				{
					"type": "entries",
					"name": "Size",
					"entries": [
						"Aasimar are built like well-proportioned humans. Your size is Medium."
					]
				},
				{
					"name": "Darkvision",
					"entries": [
						"Thanks to your celestial heritage, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light. You can't discern color in darkness, only shades of grey."
					],
					"type": "entries"
				},
				{
					"name": "Celestial Resistance",
					"entries": [
						"You have resistance to necrotic and radiant damage."
					],
					"type": "entries"
				},
				{
					"name": "Celestial Legacy",
					"entries": [
						"You know the {@spell light} cantrip. Once you reach 3rd level, you can cast the {@spell lesser restoration} spell once with this trait, and you regain the ability to do so when you finish a long rest. Once you reach 5th level, you can cast the {@spell daylight} spell once with this trait, and you regain the ability to do so when you finish a long rest. Charisma is your spellcasting ability for these spells."
					],
					"type": "entries"
				},
				{
					"name": "Language",
					"entries": [
						"You can speak, read, and write Common and Celestial."
					],
					"type": "entries"
				}
			]
		}
    
    base, document, liens = parser.parse(aasimar)

    assert base["speed"] == 30
    assert "spell:light:phb" in liens
    assert "Darkvision" in document
    assert "M" in base["size"]