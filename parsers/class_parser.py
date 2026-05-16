from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags


class ClassParser(BaseParser):
    """Parser pour les classFeature 5etools (une entité = une capacité de classe)."""

    def __init__(self, entity_type="class"):
        """Initialise le parser avec le type class."""
        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'une capacité de classe 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: class-fighter.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, className, classSource, level).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.

        Note:
            ⚠️ Backlog : parsing incomplet — startingProficiencies, HD, spellcastingAbility non inclus.
        """
        base = super().parse(data)  # récupère name, source, page
        base["className"] = data.get("className")
        base["classSource"] = data.get("classSource")
        base["level"] = data.get("level")

        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens

        document = f"""
            Name: {base["name"]}
            Classe Name: {data.get("className")}
            Classe Source: {data.get("classSource")}
            Level: {data.get('level')}
            {"\n".join(all_text)}
            """


        return base, document, all_links