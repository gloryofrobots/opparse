import re

from opparse import nodes


def keyword(literal):
    return re.compile('\\b%s\\b' % literal)


def token(literal):
    return re.compile(literal)


class Lexicon:

    """
    child classes mast describe token and node types
    in manner of class variables

    TT_NAME = "TT_NAME"
    TT_FUNCTION = "TT_FUNCTION"
    TT_ADD = "TT_ADD"

    NT_NAME = "NT_NAME"
    NT_FUNCTION = "NT_FUNCTION"
    NT_ADD = "NT_ADD"

    mapping dictionary for simple operators if one token
    type directly corepsonds to another node type

    TT_TO_NT_MAPPING = {TT_NAME:NT_NAME, TT_ADD:NT_ADD}

    tokenizer rules
    RULES = [
        (keyword("function"), TT_FUNCTION),
        (keyword("fun"), TT_FUNCTION),
        (token("[0-9]+", TT_INT),
    ]
    """
    # DEFAULTS
    TT_UNKNOWN = 1
    TT_ENDSTREAM = 0
    TT_TO_NT_MAPPING = {}
    RULES = {}