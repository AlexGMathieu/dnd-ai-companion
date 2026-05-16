import sys

sys.path.append("../parsers")
from tag_resolver import resoud_tags

def test_tag_resolver_texte():
    texte_test = "The goblin throws a {@item javelin|phb} and deals {@damage 1d6} damage."
    
    texte, liens = resoud_tags(texte_test)
    
    assert "1d6" in texte
    assert "item:javelin:phb" in liens
    assert "javelin" in texte


def test_tag_resolver_liens():
    texte_test = "{@skill Arcana}"
    
    texte, liens = resoud_tags(texte_test)

    assert "skill:arcana:xphb" in liens
    assert len(liens) == 1

def test_tag_resolver_liens3():
    texte_test = "{@creature animated object (tiny)|phb|Tiny}"
    
    texte, liens = resoud_tags(texte_test)

    assert "monster:animated object (tiny):phb" in liens
    assert len(liens) == 1

def test_tag_resolver_liens_book():
    texte_test = "{@book Classes|PHB|3}"
    
    texte, liens = resoud_tags(texte_test)

    assert "book:phb:3:none" in liens
    assert len(liens) == 1
