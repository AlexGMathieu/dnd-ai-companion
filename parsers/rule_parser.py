from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

FEATURE_TYPE_TO_FULL = {
    "AI": "Artificer Infusion",
    "ED": "Elemental Discipline",
    "EI": "Eldritch Invocation",
    "MM": "Metamagic",
    "AS": "Arcane Shot",
    "PB": "Pact Boon",
    "RN": "Rune Knight Rune",
    "RP": "Renown Perk",
}

class RuleParser(BaseParser):
    """Parser pour les entités règle variante 5etools."""

    def __init__(self, entity_type="rule"):
        """Initialise le parser avec le type rule."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'une règle variante 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: variantrules.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, ruleType, time, ability, subtype, featureType).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)
        base["ruleType"] = data.get("ruleType", None)
        base["time"] = str(data.get("time", None))
        base["ability"] = data.get("ability", None)
        base["subtype"] = data.get("type", None)
        base["featureType"] = data.get("featureType", None)  # → ["EI"]

        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens

        feature_labels = [FEATURE_TYPE_TO_FULL.get(ft, ft) for ft in data.get("featureType", [])]

        document = f"""
            Name: {data['name']}
            Type: {self.entity_type}
            Source: {data.get('source')}
            Ability: {data.get("ability")}
            Rule Type: {data.get("ruleType")}
            {"\n".join(all_text)}
            Subtype: {data.get("type", None)}
            Label: {", ".join(feature_labels)} 
            """      
        return base, document, all_links



