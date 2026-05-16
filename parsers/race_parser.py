from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags


class RaceParser(BaseParser):
    """Parser pour les entités race 5etools."""

    def __init__(self, entity_type="race"):
        """Initialise le parser avec le type race."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'une race 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: races.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, size, speed, ability, traitTags).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)  # récupère name, source, page
        base["size"] = data.get("size")
        base["speed"] = data.get("speed")
        base["ability"] = str(data.get("ability"))
        base["traitTags"] = str(data.get("traitTags"))

        all_text = []
        all_links = []
        textes = extraire_textes(data.get("entries", []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        
        if isinstance(base["speed"], dict):
            base["speed"] = str(base["speed"])


        document = f"""
            Name: {data["name"]}
            Size: {data.get("size")}
            Speed: {base["speed"]}
            Ability: {data.get("ability")}
            Traits: {data.get("traitTags")}
            {"\n".join(all_text)}
            """      
        return base, document, all_links