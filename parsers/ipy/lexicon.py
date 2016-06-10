from opparse.lexicon import Lexicon, token, keyword


class IpyLexicon(Lexicon):

    # NODE_TYPES
    NT_TRUE = "NT_TRUE"
    NT_FALSE = "NT_FALSE"
    NT_NONE = "NT_NONE"
    NT_INT = "NT_INT"
    NT_STR = "NT_STR"
    NT_MULTI_STR = "NT_MULTI_STR"
    NT_NAME = "NT_NAME"
    NT_DICT = "NT_DICT"
    NT_LIST = "NT_LIST"
    NT_TUPLE = "NT_TUPLE"
    NT_FUN = "NT_FUN"
    NT_IF = "NT_IF"
    NT_TRY = "NT_TRY"
    NT_FOR = "NT_FOR"
    NT_WHILE = "NT_WHILE"
    NT_RAISE = "NT_RAISE"
    NT_ASSIGN = "NT_ASSIGN"
    NT_PLUS_ASSIGN = "NT_PLUS_ASSIGN"
    NT_MINUS_ASSIGN = "NT_MINUS_ASSIGN"
    NT_CALL = "NT_CALL"
    NT_DOT = "NT_DOT"
    NT_COMMA = "NT_COMMA"
    NT_AS = "NT_AS"
    NT_AND = "NT_AND"
    NT_OR = "NT_OR"
    NT_NOT = "NT_NOT"
    NT_END_EXPR = "NT_END_EXPR"
    NT_END = "NT_END"

    NT_GT = "NT_GT"
    NT_GE = "NT_GE"
    NT_LE = "NT_LE"
    NT_LT = "NT_LT"
    NT_EQ = "NT_EQ"
    NT_NE = "NT_NE"
    NT_IN = "NT_IN"
    NT_IS = "NT_IS"
    NT_IS_NOT = "NT_IS_NOT"
    NT_NOT_IN = "NT_NOT_IN"

    NT_ADD = "NT_ADD"
    NT_SUB = "NT_SUB"
    NT_DIV = "NT_DIV"
    NT_MUL = "NT_MUL"
    NT_POW = "NT_POW"
    NT_MOD = "NT_MOD"

    NT_NEGATE = "NT_NEGATE"

    NT_VARGS = "NT_VARGS"
    NT_KVARGS = "NT_KVARGS"

    # TOKEN TYPES

    TT_INT = "TT_INT"
    TT_STR = "TT_STR"
    TT_NAME = "TT_NAME"
    TT_FUN = "TT_FUN"
    TT_FOR = "TT_FOR"
    TT_WHILE = "TT_WHILE"
    TT_CLASS = "TT_CLASS"
    TT_DEF = "TT_DEF"
    TT_IF = "TT_IF"
    TT_ELIF = "TT_ELIF"
    TT_ELSE = "TT_ELSE"
    TT_IN = "TT_IN"
    TT_AS = "TT_AS"
    TT_IS = "TT_IS"
    TT_IS_NOT = "TT_IS_NOT"
    TT_NOT_IN = "TT_NOT_IN"

    TT_AND = "TT_AND"
    TT_NOT = "TT_AND"
    TT_OR = "TT_OR"
    TT_TRUE = "TT_TRUE"
    TT_FALSE = "TT_FALSE"
    TT_NONE = "TT_NONE"
    TT_TRY = "TT_TRY"
    TT_RAISE = "TT_RAISE"
    TT_YIELD = "TT_YIELD"
    TT_RETURN = "TT_RETURN"
    TT_EXCEPT = "TT_EXCEPT"
    TT_FINALLY = "TT_FINALLY"
    TT_END = "TT_END"
    TT_END_EXPR = "TT_END_EXPR"
    TT_INDENT = "TT_INDENT"
    TT_NEWLINE = "TT_NEWLINE"
    TT_LAMBDA = "TT_LAMBDA"
    TT_LCURLY = "TT_LCURLY"
    TT_RCURLY = "TT_RCURLY"
    TT_COMMA = "TT_COMMA"
    TT_ASSIGN = "TT_ASSIGN"
    TT_PLUS_ASSIGN = "TT_PLUS_ASSIGN"
    TT_MINUS_ASSIGN = "TT_MINUS_ASSIGN"
    TT_LPAREN = "TT_LPAREN"
    TT_RPAREN = "TT_RPAREN"
    TT_LSQUARE = "TT_LSQUARE"
    TT_RSQUARE = "TT_RSQUARE"
    TT_DOT = "TT_DOT"
    TT_COLON = "TT_COLON"

    TT_GT = "TT_GT"
    TT_GE = "TT_GE"
    TT_LE = "TT_LE"
    TT_LT = "TT_LT"
    TT_EQ = "TT_EQ"
    TT_NE = "TT_NE"
    TT_PLUS = "TT_PLUS"
    TT_MINUS = "TT_MINUS"
    TT_SLASH = "TT_SLASH"
    TT_STAR = "TT_STAR"
    TT_DOUBLE_STAR = "TT_DOUBLE_STAR"
    TT_PERCENTS = "TT_PERCENTS"
    TT_IMPORT = "TT_IMPORT"
    TT_FROM = "TT_FROM"

    RULES = [
        (token('\n'), TT_NEWLINE),
        (token(' '), -1),
        (token('#[^\n]*'), -1),

        (token('is[\s]+not'), TT_IS_NOT),
        (token('not[\s]+in'), TT_NOT_IN),
        (keyword('if'), TT_IF),
        (keyword('elif'), TT_ELIF),
        (keyword('else'), TT_ELSE),
        (keyword('end'), TT_END),
        (keyword('is'), TT_IS),
        (keyword('and'), TT_AND),
        (keyword('or'), TT_OR),
        (keyword('not'), TT_NOT),
        (keyword('True'), TT_TRUE),
        (keyword('False'), TT_FALSE),
        (keyword('None'), TT_NONE),

        (keyword('raise'), TT_RAISE),
        (keyword('return'), TT_RETURN),
        (keyword('yield'), TT_YIELD),
        (keyword('try'), TT_TRY),
        (keyword('except'), TT_EXCEPT),
        (keyword('finally'), TT_FINALLY),
        (keyword('lambda'), TT_LAMBDA),
        (keyword('fun'), TT_FUN),
        (keyword('def'), TT_DEF),

        (keyword('class'), TT_CLASS),
        (keyword('while'), TT_WHILE),
        (keyword('for'), TT_FOR),
        (keyword('in'), TT_IN),

        (keyword('import'), TT_IMPORT),
        (keyword('from'), TT_FROM),
        (keyword('as'), TT_AS),

        (token("[0-9]+"), TT_INT),
        (token('"([^\\\"]+|\\.)*"'), TT_STR),
        (token('[a-zA-Z_][0-9a-zA-Z_]*'), TT_NAME),
        (token('\;'), TT_END_EXPR),
        (token('\{'), TT_LCURLY),
        (token('\}'), TT_RCURLY),
        (token('\,'), TT_COMMA),
        (token('\('), TT_LPAREN),
        (token('\)'), TT_RPAREN),
        (token('\['), TT_LSQUARE),
        (token('\]'), TT_RSQUARE),
        (token('\.'), TT_DOT),
        (token(':'), TT_COLON),

        (token('\+='), TT_PLUS_ASSIGN),
        (token('\-='), TT_MINUS_ASSIGN),
        (token('\*\*'), TT_DOUBLE_STAR),
        (token('=='), TT_EQ),
        (token('>='), TT_GE),
        (token('>'), TT_GT),
        (token('<'), TT_LT),
        (token('<='), TT_LE),
        (token('=='), TT_EQ),
        (token('!='), TT_NE),

        (token('\+'), TT_PLUS),
        (token('\-'), TT_MINUS),
        (token('\*'), TT_STAR),
        (token('\/'), TT_SLASH),
        (token('\%'), TT_PERCENTS),
        (token('='), TT_ASSIGN),
    ]

    TERM_BLOCK = [TT_END]
    TERM_EXP = [TT_END_EXPR]
    TERM_CONDITION = [TT_COLON]

    TERM_IF_BODY = [TT_ELSE, TT_ELIF]

    TERM_TRY = [TT_EXCEPT]
    TERM_EXCEPT = [TT_FINALLY, TT_EXCEPT] + TERM_BLOCK

    TERM_FUN_SIGNATURE = [TT_COLON]

    TERM_FOR_CONDITION = [TT_IN]
    
    TERM_FROM_IMPORTED = [TT_IMPORT]

    LEVELS_IF = [TT_ELSE, TT_ELIF]
    LEVELS_TRY = [TT_EXCEPT, TT_FINALLY]
    LEVELS_FOR = [TT_ELSE]

    ASSIGNMENT_TOKENS = [TT_ASSIGN, TT_PLUS_ASSIGN, TT_MINUS_ASSIGN]