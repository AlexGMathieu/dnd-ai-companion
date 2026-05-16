from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags


class BackgroundParser(BaseParser):
    """Parser pour les entités historique 5etools."""

    def __init__(self, entity_type="background"):
        """Initialise le parser avec le type background."""

        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un historique 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: backgrounds.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, ability, skill_proficiency, tool_proficiency, feats).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)  # récupère name, source, page
        
        ability = None
        ability_data = data.get("ability", [])
        if ability_data:
            if "choose" in ability_data[0]:
                ability = ", ".join(ability_data[0]["choose"]["weighted"]["from"])
            else:
                ability = ", ".join(ability_data[0].keys())
            base["ability"] = ability

        skill_proefficiencies = None
        skill_proefficiencies_data = data.get("skillProficiencies", [])
        if skill_proefficiencies_data:
            skill_proefficiencies = ", ".join(skill_proefficiencies_data[0].keys())
            base["skill_proefficiencies"] = skill_proefficiencies

        tool_proefficiencies = None
        tool_proefficiencies_data = data.get("toolProficiencies", [])
        if tool_proefficiencies_data:
            tool_proefficiencies = ", ".join(tool_proefficiencies_data[0].keys())
            base["tool_proefficiencies"] = tool_proefficiencies

        feats = None
        feats_data = data.get("feats", [])
        if feats_data:
            feats = ", ".join(feats_data[0].keys())
            base["feats"] = feats
        
        all_text = []
        all_links = []
        textes = extraire_textes(data.get('entries', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens

        document = f"""
            Name: {base["name"]}
            Ability: {ability}
            Skill Proefficiencies: {skill_proefficiencies}
            Toll Proefficiencies: {tool_proefficiencies}
            Feats: {feats}
            {"\n".join(all_text)}
            """    

        return base, document, all_links






