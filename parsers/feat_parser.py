import json
from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

class FeatParser(BaseParser):
    """Parser pour les entités don 5etools."""

    def __init__(self, entity_type="feat"):
        """Initialise le parser avec le type feat."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un don 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: feats.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, category).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)
        base["category"] = data.get("category")

        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        prereq_text = json.dumps(data.get("prerequisite", []))
        all_text.append(prereq_text)
        additional_spells_text = json.dumps(data.get("additionalSpells", []))
        all_text.append(additional_spells_text)

        document = f"""
            Name: {data['name']}
            Type: {self.entity_type}
            Source: {data.get('source')}
            Category: {data.get("category")}
            {"\n".join(all_text)}
            """      
        return base, document, all_links
    
