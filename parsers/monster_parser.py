import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from base_parser import BaseParser
from text_extractor import extraire_textes
from tag_resolver import resoud_tags

# def format_actions(actions):
#     lignes = []
#     for action in actions:
#         lignes.append(f'{action["name"]}, {" ".join(extraire_textes(action.get("entries", [])))}')
#     return "\n".join(lignes)

class MonsterParser(BaseParser):
    """Parser pour les entités monstre 5etools."""

    def __init__(self, entity_type="monster"):
        """Initialise le parser avec le type monster."""

        super().__init__(entity_type)

    def parse(self, data: dict) -> tuple:
        """
        Extrait les métadonnées, le document texte et les liens internes d'un monstre 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools (ex: bestiary-mm.json).

        Returns:
            tuple:
                - base (dict): Métadonnées pour ChromaDB (name, source, cr, size, etc.).
                - document (str): Texte lisible pour la recherche sémantique.
                - all_links (list): Liens internes au format type:nom:source.
        """
        base = super().parse(data)  # récupère name, source, page

        cr = data.get('cr')  # peut être None, str, ou dict

        if cr is None:
            data_cr = None
        elif type(cr) == dict:
            data_cr = cr.get('cr')
        else:
            data_cr = cr

        base["cr"] = data_cr
        base["size"] = str(data.get("size"))
        base["environment"] = str(data.get("environment"))
        base["image_path"] = f"bestiary/{data['source']}/{data['name']}.webp" if data.get("hasToken") else None
        base["has_fluff"] = data.get("hasFluff")
        
        all_text = []
        all_links = []
        textes = extraire_textes(data.get('trait', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('action', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('legendary', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens
        textes = extraire_textes(data.get('variant', []))
        for texte in textes:
            text, liens = resoud_tags(texte)
            all_text.append(text)
            all_links += liens


        if type(data['type']) == dict:
            data_type = data.get('type', {}).get('type')
        else:
            data_type = data['type']
        document = f"""
            Name: {data['name']}
            Type: {data_type}
            Speed: {data.get('speed')}
            {"\n".join(all_text)}
            """      
        return base, document, all_links


