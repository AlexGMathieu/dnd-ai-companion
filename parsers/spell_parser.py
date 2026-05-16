from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

class SpellParser(BaseParser):
    """Parser pour les entités sort 5etools."""

    def __init__(self, entity_type="spell"):
        """Initialise le parser avec le type spell."""

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un sort 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: spells-phb.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, level, school, time, range, components, duration, classes).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)
        base["level"] = data.get("level")
        base["school"] = data.get("school")
        base["time"] = str(data.get("time"))
        base["range"] = str(data.get("range"))
        base["components"] = str(data.get("components"))
        base["duration"] = str(data.get("duration"))
        base["classes"] = str([])

        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            _, liens = resoud_tags(texte)
            all_links += liens
        textes = extraire_textes(data.get('entriesHigherLevel', []))
        for texte in textes:
            _, liens = resoud_tags(texte)
            all_links += liens

        document = f"""
            Name: {data['name']}
            Level: {data.get('level')}
            School: {data.get('school')}
            Range: {data.get('range')}
            Casting Time: {data.get('time')}
            Components: {data.get('components')}
            Duration: {data.get('duration')}
            {"\n".join(extraire_textes(data.get('entries', [])))}
            At Higher Levels: {"\n".join(extraire_textes(data.get('entriesHigherLevel', [])))}
            Classes: {base["classes"]}
            """      
        return base, document, all_links
