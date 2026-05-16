import re

ATK_TRADUCTIONS = {
    'mw': 'Melee Weapon Attack',
    'rw': 'Ranged Weapon Attack',
    'mw,rw': 'Melee or Ranged Weapon Attack',
    'ms': 'Melee Spell Attack',
    'rs': 'Ranged Spell Attack'
}

TAG_VERS_TYPE = {
    'creature': 'monster',
    'item': 'item',
    'spell': 'spell',
    'action': 'action',
    'status': 'condition',
    'variantrule': 'rule',
    'condition' :'condition',
    'book': 'book',
    'class': 'class',
    'adventure': 'adventure',
    'vehupgrade': 'vehupgrade',
    'table': 'table',
    'card': 'card',
    'vehicle': 'vehicle',
    'trap': 'trap',
    'skill': 'skill',
    'sense': 'sense',
    'quickref': 'rule'
}

SOURCE_PAR_DEFAUT = {
    'creature': 'mm',
    'item': 'phb',
    'spell': 'phb',
    'action': 'xphb',
    'status': 'phb',
    'variantrule': 'variantrule',
    'condition': 'phb',
    'book': 'phb',
    'class': 'phb',
    'adventure': 'phb',
    'vehupgrade': 'gos',
    'table': 'dmg',
    'card': 'cos',
    'vehicle': 'gos',
    'trap': 'vrgr',
    'skill': 'xphb',
    'sense': 'xphb',
    'quickref': 'variantrule'
}

def detecte_tags(texte) -> list:
    """
    Détecte les patterns de tags

    Args:
        texte (str) : une chaine de caractère issue d'un texte brut extrait d'un JSON 5etools
    
    Returns:
        Une liste de tuples (tag, contenu)
    
    Example:
        >>> detecte_tags("{@item Javelin|PHB}")
        [('item', 'Javelin|PHB')]
    """
    tags_sans_contenu = re.findall(r"\{@(\w+)\}", texte)
    tags = re.findall(r"\{@(\w+) (.+?)\}", texte) + [(tag, '') for tag in tags_sans_contenu]    
    return tags

def detecte_tags_formatage(tag) -> str:
    """
    Formate un tag de formatage 5etools en texte lisible.

    Args:
        tag (tuple): Un tuple (type, contenu).

    Returns:
        str: Le texte formaté.

    Example:
        >>> detecte_tags_formatage(('damage', '1d6'))
        '1d6'
        >>> detecte_tags_formatage(('hit', '9'))
        '+9'
        >>> detecte_tags_formatage(('atk', 'mw'))
        'Melee Weapon Attack'
        >>> detecte_tags_formatage(('atk', 'ms'))
        'Melee Spell Attack'
        >>> detecte_tags_formatage(('chance', '50'))
        '50%'
        >>> detecte_tags_formatage(('dc', '15'))
        'DC 15'
    """
    if tag[0] in ['damage', 'dice']:
        return tag[-1]
    elif tag[0] in ['b', 'bold', 'i', 'note', 'link', '5etools', 'hazard', 'deck', 'filter']:
        return tag[1]
    elif tag[0] == 'h':
        return ''
    elif tag[0] == 'hit':
        return '+' + tag[1]
    elif tag[0] == 'atk':
        return ATK_TRADUCTIONS[tag[1]]
    elif tag[0] == 'chance':
        return tag[1] + '%'
    elif tag[0] == 'dc':
        return 'DC ' + tag[1]
    else:
        # raise ValueError(f"Tag formatage inconnu : {tag[0]}")
        return tag[1]

def detecte_tags_liens(tag) -> str:
    """
    Convertit un tag de lien 5etools en ID stable type:nom:source.

    ...

    Format des tags selon le nombre de parties après split("|") :

        len == 1 : {@creature goblin}
                → 'monster:goblin:mm'

        len == 2 (rempli) : {@item plate armor|phb}
                → 'item:plate armor:phb'

        len == 2 (vide) : {@creature goblin|}
                → 'monster:goblin:mm'

        len == 3 : {@creature animated object (tiny)|phb|Tiny}
                → 'monster:animated object (tiny):phb'

        len == 4 : {@quickref Cover||3||total cover}
                → 'rule:cover:variantrule'

        len == 5 : cas générique → type:nom:source
        
        len == 6 : {@class Fighter|phb|...} → type:nom:source
                ⚠️ Backlog : retourner deux liens (classe + sous-classe)

        book/adventure : format dédié → type:source:chapter:anchor

    ...
    """
    if tag[0] in ['book', 'adventure']:
        contenu_tag = tag[1].split("|")
        contenu_tag = [x for x in contenu_tag if x != '']
        if len(contenu_tag) == 2:
            source = contenu_tag[1] if contenu_tag[1] != '' else SOURCE_PAR_DEFAUT[tag[0]]
            return f"{TAG_VERS_TYPE[tag[0]]}:{source}:none:none".lower()
        elif len(contenu_tag) == 3:
            source = contenu_tag[1] if contenu_tag[1] != '' else SOURCE_PAR_DEFAUT[tag[0]]
            return f"{TAG_VERS_TYPE[tag[0]]}:{source}:{contenu_tag[2]}:none".lower()
        elif len(contenu_tag) == 4:
            source = contenu_tag[1] if contenu_tag[1] != '' else SOURCE_PAR_DEFAUT[tag[0]]
            return f"{TAG_VERS_TYPE[tag[0]]}:{source}:{contenu_tag[2]}:{contenu_tag[3]}".lower()
        elif len(contenu_tag) == 1:
            return f"{TAG_VERS_TYPE[tag[0]]}:{SOURCE_PAR_DEFAUT[tag[0]]}:none:none".lower()
    else:
        contenu_tag = tag[1].split("|")
        if len(contenu_tag) == 2:
            nom = contenu_tag[0]
            if contenu_tag[1] != '':
                source = contenu_tag[1]
            else:
                source = SOURCE_PAR_DEFAUT[tag[0]]
        elif len(contenu_tag) == 1:
            nom =  contenu_tag[0]
            source = SOURCE_PAR_DEFAUT[tag[0]]
        elif len(contenu_tag) == 3:
            nom =  contenu_tag[0]
            if contenu_tag[1] != '':
                source = contenu_tag[1]
            else:
                source = SOURCE_PAR_DEFAUT[tag[0]]
        elif len(contenu_tag) == 4:
            nom =  contenu_tag[0]
            source = SOURCE_PAR_DEFAUT[tag[0]]
        elif len(contenu_tag) == 5:
            nom =  contenu_tag[0]
            source = SOURCE_PAR_DEFAUT[tag[0]]
        elif len(contenu_tag) == 6:
            nom = contenu_tag[0]
            source = contenu_tag[1]
        else:
            raise ValueError(f"Format de tag inattendu : {tag}")
        return f"{TAG_VERS_TYPE[tag[0]]}:{nom}:{source}".lower()


def resoud_tags(texte) -> tuple:
    """
    Détecte les patterns de tags, détecte s'il s'agit d'un tag de formatage ou de lien, 
    et retourne un tuple de chaine de caractères

    Args:
        texte (str) : une chaine de caractère issue d'un texte brut extrait d'un JSON 5etool
    
    Returns:
        tuple (texte, liens) :
            - texte (str): la string originale avec les tags remplacés par le nom canonique
            - liens (list): une liste d'IDs stables au format type:nom:source

    Examples:
        Tags de formatage (nettoyés en texte lisible) :

        {@damage 1d6}   → '1d6'
        {@dice 2d4}     → '2d4'
        {@hit 9}        → '+9'
        {@atk mw}       → 'Melee Weapon Attack'
        {@h}            → '' (vide)

        Tags de liens (convertis en IDs stables type:nom:source) :

        {@creature goblin|mm}   → 'monster:goblin:mm'
        {@item javelin|phb}     → 'item:javelin:phb'
        {@spell fireball|phb}   → 'spell:fireball:phb'
    """
    liens = []
    tags = detecte_tags(texte)
    for tag in tags:
        if tag[0] in TAG_VERS_TYPE:
            liens.append(detecte_tags_liens(tag))
            contenu_tag = tag[1].split("|")
            nom = contenu_tag[0]
            texte = texte.replace("{@" + tag[0] + " " + tag[1] + "}", nom)
        else:
            if tag[1] != '':
                ancien = "{@" + tag[0] + " " + tag[1] + "}"
            else:
                ancien = "{@" + tag[0] + "}"
            texte = texte.replace(ancien, detecte_tags_formatage(tag))
        
    return (texte, liens)

