class BaseParser:
    """Classe parent commune à tous les parsers 5etools."""

    def __init__(self, entity_type="unknown"):
        """
        Initialise le parser avec le type d'entité.
        
        Args:
            entity_type (str): Type de l'entité 5etools (ex: rule, monster, item, etc.). Defaults to "unknown".
        """
        self.entity_type = entity_type

    def parse(self, data: dict) -> dict:
        """
        Extrait les champs communs à toutes les entités 5etools.

        Args:
            data (dict): Données brutes issues d'un JSON 5etools.

        Returns:
            dict: Métadonnées communes (entity_type, name, source, page).
        """
        return {
            "entity_type": self.entity_type,
            "name": data["name"],
            "source": data["source"],
            "page": data.get("page"),
        }
