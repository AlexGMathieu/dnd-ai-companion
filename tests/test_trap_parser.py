import pytest
import sys

sys.path.append("../parsers")
from trap_parser import TrapParser

parser = TrapParser()

def test_trap_parser_balance():
    balance_and_ruin = {
			"name": "Balance and Ruin",
			"source": "BMT",
			"page": 29,
			"trapHazType": "MECH",
			"rating": [
				{
					"tier": 2,
					"threat": "deadly"
				}
			],
			"entries": [
				{
					"type": "inset",
					"entries": [
						"A narrow wooden beam spans the length of this hundred-foot-long, fifty-foot-wide chamber. The beam crosses a twenty-five-foot-deep pit filled with slowly turning, bloodstained gears. The chamber's side walls, each 25 feet from the balance beam, are made of smooth metal sheeting."
					]
				},
				"The most obvious way to cross the room is to walk along the beam. But there's a hidden danger: a pressure plate beneath the beam's closest end causes the metal walls to emit a strong magnetic field.",
				{
					"type": "entries",
					"name": "Fulcrum",
					"entries": [
						"Stone pillars set at regular intervals appear to hold up the beam. But the pillar beneath the beam's center is a fulcrum (like the center of a seesaw), which gives the beam a nearly indiscernible tilt. A creature that examines the beam and succeeds on a {@dc 15} Intelligence ({@skill Investigation}) check notices the tilt. When the characters enter the room, the beam's weight rests on the far end. When any amount of weight is placed on the stretch of beam between the characters and the fulcrum, unless a counterweight is placed on the opposite side, the end of the beam sinks a few inches and presses on a hidden pressure plate. If all the weight is removed from the beam at once, the beam remains in whatever position it was last in."
					]
				},
				{
					"type": "entries",
					"name": "Balance Beam",
					"entries": [
						"The balance beam is {@book difficult terrain|PHB|8|Difficult Terrain}. A creature that ends its turn on the beam or that is on the beam when it tilts must make a {@dc 12} Dexterity saving throw to keep its balance. If the walls are magnetized (see below) and the creature is wearing metal armor or holding metal equipment, the creature has disadvantage on this save. A creature that fails the save by 4 or less slips, landing on the beam, and has the {@condition prone} condition. A creature that fails this save by 5 or more falls into the gear pit (see \"Gear Pit\" below)."
					]
				},
				{
					"type": "entries",
					"name": "Magnetic Walls",
					"entries": [
						"When the balance beam's weight is on the pressure plate, the metal walls emit a magnetic field. Any creature wearing metal armor or holding metal equipment who isn't on the beam is pulled to the nearest metal wall and sticks to it, taking 11 ({@damage 2d10}) bludgeoning damage. Any creature stuck to the wall has the {@condition restrained} condition until the magnetic field deactivates. Removing pressure from the plate\u2014such as by putting more weight on the opposite end of the beam\u2014deactivates the magnetic field. If the whole party has access to flight, you can make the trap suitably challenging by removing the pressure plate and having the magnetic field toggle on or off in 1-minute intervals or whenever a creature ends its turn on a different side of the pit from where it started. A character wearing metal armor or holding metal equipment who flies across the hall while the walls are magnetized is pulled to the wall and stuck to it."
					]
				},
				{
					"type": "entries",
					"name": "Gear Pit",
					"entries": [
						"Whenever a creature falls into the pit or ends its turn there, that creature must succeed on a {@dc 17} Dexterity saving throw or take 55 ({@damage 10d10}) bludgeoning damage and have the {@condition prone} condition. A creature that is {@condition prone} on the gears can't use movement to stand up without first using an action and a Tiny object to jam the gears below it. Those gears remain jammed until the end of the character's turn, whereupon the Tiny object tumbles loose, falls through the gears, and is lost."
					]
				}
			],
			"hasFluffImages": True
		}
    
    base, document, liens = parser.parse(balance_and_ruin)

    assert "Balance and Ruin" in base["name"]
    assert "threat" in document
    assert "MECH" in base["trapHazType"]
    assert "Whenever a creature falls into the pit or ends its turn there" in document
    assert "condition:prone:phb" in liens


def test_trap_parser_bear():
    bear_trap = {
			"name": "Bear Trap",
			"source": "XGE",
			"page": 113,
			"trapHazType": "SMPL",
			"rating": [
				{
					"tier": 1,
					"threat": "dangerous"
				}
			],
			"effect": [
				"{@atk mw} {@hit 8} to hit, triggering creature. Hit: 5 ({@damage 1d10}) piercing damage. This attack can't gain advantage or disadvantage. A creature hit by the trap has its speed reduced to 0. It can't move until it breaks free of the trap, which requires a successful {@dc 15} Strength check by the creature or another creature adjacent to the trap."
			],
			"trigger": [
				"A creature that steps on the bear trap triggers it."
			],
			"countermeasures": [
				"A successful {@dc 10} Wisdom ({@skill Perception}) check reveals the trap. A successful {@dc 10} Dexterity check using {@item thieves' tools|phb} disables it."
			],
			"entries": [
				"A bear trap resembles a set of iron jaws that springs shut when stepped on, clamping down on a creature's leg. The trap is spiked in the ground, leaving the victim immobilized."
			]
		}
    base, document, liens = parser.parse(bear_trap)

    assert "Bear Trap" in base["name"]
    assert "threat" in document
    assert "SMPL" in base["trapHazType"]
    assert "A creature that steps on the bear trap triggers it." in document
    assert "skill:perception:xphb" in liens