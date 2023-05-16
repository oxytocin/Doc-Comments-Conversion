import pytest
from convert import *

def test_find_unescaped():
    with pytest.raises(ValueError):
        find_unescaped("", "[")
    with pytest.raises(ValueError):
        find_unescaped(r"\[", "[")
    with pytest.raises(ValueError):
        find_unescaped(r"l\[", "[")
    with pytest.raises(ValueError):
        find_unescaped(r"lo\[", "[")
    with pytest.raises(ValueError):
        find_unescaped(r"lol \\\[xd]", "[")
    assert find_unescaped("[", "[") == 0
    assert find_unescaped("l[", "[") == 1
    assert find_unescaped("ll[", "[") == 2
    assert find_unescaped(r"\\[", "[") == 2
    assert find_unescaped(r"\[ [", "[") == 3

    assert find_unescaped("help [ lol [ lol", "[", 12, reverse=True) == 11

def test_find_between_delimiters():
    assert between_delimiters("[lol]", 1, "[", "]") == True
    assert between_delimiters("[xd] [lol] [xd]", 6, "[", "]") == True
    assert between_delimiters("[lol] xd", 5, "[", "]") == False
    assert between_delimiters("[dx] lol [xd]", 5, "[", "]") == False

def test_split_pandoc_text_on_lines():
    assert split_pandoc_text_on_lines("lol\nlmao[lm\nfao]") == ['lol', 'lmao[lm\nfao]']

def test_preceeding_backslashes():
    assert preceeding_backslashes("", 0) == 0
    assert preceeding_backslashes("\\t", 1) == 1
    assert preceeding_backslashes("\\\\t", 2) == 2
    assert preceeding_backslashes("\\\\t \\l", 5) == 1
