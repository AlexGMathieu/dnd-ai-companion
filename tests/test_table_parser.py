import pytest
import sys

sys.path.append("../parsers")
from table_parser import TableParser

parser = TableParser()

def test_table_parser_manifestations():
    manifestations = 		{
			"name": "Beneficial Manifestations",
			"source": "AitFR-AVT",
			"page": 12,
			"otherSources": [
				{
					"source": "AitFR-DN",
					"page": 14
				},
				{
					"source": "AitFR-FCD",
					"page": 15
				}
			],
			"caption": "Beneficial Manifestations",
			"colLabels": [
				"d100",
				"Manifestation"
			],
			"colStyles": [
				"col-2 text-center",
				"col-10"
			],
			"rows": [
				[
					"01\u201320",
					"Your creation has a smell that is pleasing to you, even if there is no source for it."
				],
				[
					"21\u201330",
					"You can spend 1 minute to dispel any lightly obscuring conditions within 120 feet in your creation."
				],
				[
					"31\u201340",
					"Within your creation, you can cast create food and water once per day without using a spell slot."
				],
				[
					"41\u201350",
					"You can understand any language spoken within 30 feet of you while within your creation."
				],
				[
					"51\u201360",
					"Beasts find your creation appealing or off-putting (you decide)."
				],
				[
					"61\u201370",
					"When your creation is made, you decide what weather is possible within it."
				],
				[
					"71\u201380",
					"You cannot be charmed or frightened while within your creation."
				],
				[
					"81\u201390",
					"All structures in your creation have +2 AC."
				],
				[
					"91\u201300",
					"You have advantage on your passive Perception score within your creation."
				]
			]
		}
    
    base, document, liens = parser.parse(manifestations)

    assert "Beneficial Manifestations" in base["name"]
    assert "AitFR-AVT" in base["source"]
    assert "d100" in document
    assert "All structures in your creation have +2 AC." in document

def test_table_parser_objets():
    objets = 		{
			"name": "250 gp Art Objects",
			"source": "PSX",
			"page": 24,
			"caption": "250 gp Art Objects",
			"colLabels": [
				"d10",
				"Object"
			],
			"colStyles": [
				"col-2 text-center",
				"col-10"
			],
			"rows": [
				[
					"1",
					"{@item Silver necklace with an amber pendant (Sun Empire)|psx}"
				],
				[
					"2",
					"{@item Fine robe with dinosaur feathers and silver embroidery (Sun Empire)|psx}"
				],
				[
					"3",
					"{@item Jade headpiece (River Heralds)|psx}"
				],
				[
					"4",
					"{@item Carved jade statuette (River Heralds)|psx}"
				],
				[
					"5",
					"{@item Jade bowl (River Heralds)|psx}"
				],
				[
					"6",
					"{@item Bronze spyglass (Brazen Coalition)|psx}"
				],
				[
					"7",
					"{@item Pewter mug with green spinels (Brazen Coalition)|psx}"
				],
				[
					"8",
					"{@item Gold pendant with black onyx (Legion of Dusk)|psx}"
				],
				[
					"9",
					"{@item Large well-made tapestry (Legion of Dusk)|psx}"
				],
				[
					"10",
					"{@item Large gold bracelet (Legion of Dusk)|psx}"
				]
			]
		}
    base, document, liens = parser.parse(objets)

    assert "250 gp Art Objects" in base["name"]
    assert "PSX" in base["source"]
    assert "d10" in document
    assert "item:large gold bracelet (legion of dusk):psx" in liens

def test_table_parser_whirlpools():
    whirlpools = {
			"name": "Whirlpools; Whirlpool Rank",
			"source": "GoS",
			"page": 206,
			"caption": "Whirlpool Rank",
			"colLabels": [
				"Rank",
				"Diameter",
				"Velocity",
				"DC"
			],
			"colStyles": [
				"text-center col-2-1",
				"col-3-3",
				"col-3-3",
				"col-3-3 text-center"
			],
			"rows": [
				[
					"1",
					"22 ({@dice 4d10}) ft.",
					"5 ft.",
					"5"
				],
				[
					"2",
					"55 ({@dice 10d10}) ft.",
					"15 ft.",
					"10"
				],
				[
					"3",
					"110 ({@dice 20d10}) ft.",
					"25 ft.",
					"15"
				],
				[
					"4",
					"165 ({@dice 30d10}) ft.",
					"35 ft.",
					"20"
				]
			]
		}
    base, document, liens = parser.parse(whirlpools)

    assert "Whirlpools; Whirlpool Rank" in base["name"]
    assert "GoS" in base["source"]
    assert "Velocity" in document
    assert "4 | 165 (30d10) ft. | 35 ft. | 20" in document