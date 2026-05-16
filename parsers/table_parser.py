from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

class TableParser(BaseParser):
    """Parser pour les entités table 5etools."""

    def __init__(self, entity_type="table"):
        """Initialise le parser avec le type table."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'une table 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: tables.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, page).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)
        
        all_text = []
        all_links = []
        col_label = extraire_textes(data.get('colLabels', []))
        all_text.append(" | ".join(col_label))
        
        rows = data.get('rows', [])
        for row in rows:
            text, liens = resoud_tags(" | ".join(row))
            all_text.append(text)
            all_links += liens

        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens

        document = f"""
        Name: {data['name']}
        Type: {self.entity_type}
        Source: {data.get('source')}
        {"\n".join(all_text)}
        """      
        return base, document, all_links
    