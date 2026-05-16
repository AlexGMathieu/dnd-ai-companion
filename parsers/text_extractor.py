from tag_resolver import resoud_tags

def extraire_textes(entries: list) -> list:
    """
    Extrait récursivement les chaînes de caractères imbriquées dans un JSON 5etools.

    Args:
        entries (list): Liste d'entrées brutes issues d'un JSON 5etools.

    Returns:
        list[str]: Textes extraits à plat.
    """
    textes = []
    for element in entries:
        if type(element) == str:
            textes.append(element)
        elif type(element) == list:
            for row in element:
                if type(row) == str:
                    textes.append(row)
                elif type(row) == int:
                    textes.append(str(row))
                else:
                    textes += extraire_textes(
                        row.get('entries', []) + 
                        row.get('items', []) + 
                        row.get('rows', []) +
                        row.get('colLabels', [])
                    )
        else:
            textes += extraire_textes(
                element.get('entries', []) + 
                ([element.get('entry')] if element.get('entry') else []) + 
                element.get('items', []) + 
                element.get('rows', []) +
                element.get('colLabels', []) +
                ([element.get('name')] if element.get('name') else [])
                )
    return textes

def extraire_textes_et_liens(entries: list) -> tuple:
    """
    Extrait les textes et les liens internes depuis une liste d'entrées 5etools.

    Args:
        entries (list): Liste d'entrées brutes issues d'un JSON 5etools.
            Passer [] si le champ est absent (ex: data.get('trait', [])).

    Returns:
        tuple:
            - all_text (list[str]): Textes nettoyés des tags 5etools.
            - all_links (list[str]): Liens internes au format type:nom:source.
    """
    all_text = []
    all_links = []
    textes = extraire_textes(entries)
    for texte in textes:
        text, liens = resoud_tags(texte)
        all_text.append(text)
        all_links += liens
    return all_text, all_links