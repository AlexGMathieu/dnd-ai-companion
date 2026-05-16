import json
from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

class TrapParser(BaseParser):
    """Parser pour les entités piège 5etools."""

    def __init__(self, entity_type="trap"):
        """Initialise le parser avec le type trap."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un piège 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: traps-elite.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, trapHazType).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)
        base["trapHazType"] = data.get("trapHazType")

        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('trigger', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('effect', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('countermeasures', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        rating_text = json.dumps(data.get("rating", []))
        all_text.append(rating_text)


        document = f"""
            Name: {data['name']}
            Type: {self.entity_type}
            Source: {data.get('source')}
            Trap/Hazard Type: {data.get("trapHazType")}
            {"\n".join(all_text)}
            """      
        return base, document, all_links
    
