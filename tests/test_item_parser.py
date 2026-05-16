import pytest
import sys

sys.path.append("../parsers")
from item_parser import ItemParser

parser = ItemParser()



def test_item_parser():
    amulet =		{
			"name": "+1 Amulet of the Devout",
			"source": "TCE",
			"page": 119,
			"rarity": "uncommon",
			"reqAttune": "by a cleric or paladin",
			"reqAttuneTags": [
				{
					"class": "cleric"
				},
				{
					"class": "paladin"
				}
			],
			"wondrous": True,
			"weight": 1,
			"bonusSpellAttack": "+1",
			"bonusSpellSaveDc": "+1",
			"entries": [
				"This amulet bears the symbol of a deity inlaid with precious stones or metals. While you wear the holy symbol, you gain a +1 bonus to spell attack rolls and the saving throw DCs of your spells.",
				"While you wear this amulet, you can use your Channel Divinity feature without expending one of the feature's uses. Once this property is used, it can't be used again until the next dawn."
			]
		}

    base, document, liens = parser.parse(amulet)

    assert len(liens) == 0
    assert "+1 Amulet of the Devout" == base["name"]
    assert "by a cleric or paladin" == base["reqAttune"]
    assert "This amulet bears the symbol of a deity inlaid with precious stones or metals" in document

def test_item_parser_liens():
    alchemist_supply = {
			"name": "Alchemist's Supplies",
			"source": "PHB",
			"page": 154,
			"srd": True,
			"basicRules": True,
			"additionalSources": [
				{
					"source": "XGE",
					"page": 79
				}
			],
			"referenceSources": [
				"IMR",
				"JttRC",
				"KftGV",
				"OoW",
				"PaBTSO",
				"RtG",
				"SCC-ARiR",
				"TftYP-TSC",
				"ToA",
				"TTP",
				"WDMM"
			],
			"reprintedAs": [
				"Alchemist's Supplies|XPHB"
			],
			"type": "AT",
			"rarity": "none",
			"weight": 8,
			"value": 5000,
			"additionalEntries": [
				"Alchemist's supplies enable a character to produce useful concoctions, such as acid or alchemist's fire.",
				{
					"type": "entries",
					"name": "Components",
					"entries": [
						"Alchemist's supplies include two glass beakers, a metal frame to hold a beaker in place over an open flame, a glass stirring rod, a small mortar and pestle, and a pouch of common alchemical ingredients, including salt, powdered iron, and purified water."
					]
				},
				{
					"type": "entries",
					"name": "Arcana",
					"entries": [
						"Proficiency with alchemist's supplies allows you to unlock more information on {@skill Arcana} checks involving potions and similar materials."
					]
				},
				{
					"type": "entries",
					"name": "Investigation",
					"entries": [
						"When you inspect an area for clues, proficiency with alchemist's supplies grants additional insight into any chemicals or other substances that might have been used in the area."
					]
				},
				{
					"type": "entries",
					"name": "Alchemical Crafting",
					"entries": [
						"You can use this tool proficiency to create alchemical items. A character can spend money to collect raw materials, which weigh 1 pound for every 50 gp spent. The DM can allow a character to make a check using the indicated skill with advantage. As part of a long rest, you can use alchemist's supplies to make one dose of {@item acid (vial)|phb|acid}, {@item alchemist's fire (flask)|phb|alchemist's fire}, {@item antitoxin (vial)|phb|antitoxin}, {@item oil (flask)|phb|oil}, {@item perfume (vial)|phb|perfume}, or {@item soap|phb}. Subtract half the value of the created item from the total gp worth of raw materials you are carrying."
					]
				},
				{
					"type": "table",
					"caption": "Alchemist's Supplies",
					"colLabels": [
						"Activity",
						"DC"
					],
					"colStyles": [
						"col-10",
						"col-2 text-center"
					],
					"rows": [
						[
							"Create a puff of thick smoke",
							"10"
						],
						[
							"Identify a poison",
							"10"
						],
						[
							"Identify a substance",
							"15"
						],
						[
							"Start a fire",
							"15"
						],
						[
							"Neutralize acid",
							"20"
						]
					]
				}
			]
		}
    
    base, document, liens = parser.parse(alchemist_supply)

    assert "PHB" == base["source"]
    assert "Alchemist's supplies include two glass beakers" in document
    assert "Identify a poison" in document
    assert "item:acid (vial):phb" in liens
