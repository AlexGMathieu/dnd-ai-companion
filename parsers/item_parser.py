from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

ITEM_TYPE_TO_FULL = {
    "$": "Treasure",
    "$A": "Art Object",
    "$C": "Coinage",
    "$G": "Gemstone",
    "A": "Ammunition",
    "AF": "Ammunition (Futuristic)",
    "AIR": "Vehicle (Air)",
    "AT": "Artisan Tool",
    "EXP": "Explosive",
    "FD": "Food and Drink",
    "G": "Adventuring Gear",
    "GS": "Gaming Set",
    "GV": "Generic Variant",
    "HA": "Heavy Armor",
    "IDG": "Illegal Drug",
    "INS": "Instrument",
    "LA": "Light Armor",
    "M": "Melee Weapon",
    "MA": "Medium Armor",
    "MNT": "Mount",
    "OTH": "Other",
    "P": "Potion",
    "R": "Ranged Weapon",
    "RD": "Rod",
    "RG": "Ring",
    "S": "Shield",
    "SC": "Scroll",
    "SCF": "Spellcasting Focus",
    "SHP": "Vehicle (Water)",
    "SPC": "Vehicle (Space)",
    "T": "Tool",
    "TAH": "Tack and Harness",
    "TB": "Trade Bar",
    "TG": "Trade Good",
    "VEH": "Vehicle (Land)",
    "WD": "Wand",
}

class ItemParser(BaseParser):
    def __init__(self, entity_type="item"):
        """Parser pour les entités item 5etools."""

        super().__init__(entity_type)
        """Initialise le parser avec le type item."""

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un item 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: items-phb.json).

        Returns:
            tuple:
                base : est un dict pour l'indexation ChromaDB
                document : contient le texte (str) à destination du lecteur et de la recherche sémantique
                all_links : contient la liste des liens formatés type:nom:source pour garder les liens internes
        """
        base = super().parse(data)
        base["type"] = data.get("type")
        base["rarity"] = data.get("rarity")
        base["weight"] = data.get("weight")
        base["value"] = data.get("value")
        base["edition"] = data.get("edition", None)
        base["reqAttune"] = data.get("reqAttune", None)
        base["bonusSpellAttack"] = data.get("bonusSpellAttack", None)

        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('additionalEntries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens

        item_type = ITEM_TYPE_TO_FULL.get(data.get('type'), data.get('type'))

        document = f"""
            Name: {data['name']}
            Type: {item_type}
            Rarity: {data.get('rarity')}
            Weight: {data.get('weight')}
            Value: {data.get('value')}
            Edition: {data.get('edition')}
            {"\n".join(all_text)}
            Attunement: {data.get("reqAttune", None)}
            Bonus Spell Attack: {data.get("bonusSpellAttack", None)}
            """      
        return base, document, all_links



