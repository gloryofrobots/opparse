from opparse.lexicon import Lexicon, token, keyword


class LuaLexicon(Lexicon):

    # TOKEN TYPES
    TT_INT = "TT_INT"
    TT_STR = "TT_STR"
    TT_NAME = "TT_NAME"
    TT_FUNCTION = "TT_FUNCTION"
    TT_FOR = "TT_FOR"
    TT_WHILE = "TT_WHILE"

    TT_BREAK = "TT_BREAK"
    TT_CONTINUE = "TT_CONTINUE"

    TT_REPEAT = "TT_REPEAT"
    TT_UNTIL = "TT_UNTIL"
    TT_LOCAL = "TT_LOCAL"
    TT_DO = "TT_DO"

    TT_THEN = "TT_THEN"
    TT_IF = "TT_IF"
    TT_ELSE = "TT_ELSE"
    TT_ELSEIF = "TT_ELSEIF"
    TT_IN = "TT_IN"

    TT_AND = "TT_AND"
    TT_NOT = "TT_AND"
    TT_OR = "TT_OR"
    TT_TRUE = "TT_TRUE"
    TT_FALSE = "TT_FALSE"
    TT_NIL = "TT_NIL"
    TT_RETURN = "TT_RETURN"
    TT_END = "TT_END"
    TT_END_EXPR = "TT_END_EXPR"
    TT_NEWLINE = "TT_NEWLINE"
    TT_LCURLY = "TT_LCURLY"
    TT_RCURLY = "TT_RCURLY"
    TT_COMMA = "TT_COMMA"
    TT_ASSIGN = "TT_ASSIGN"
    TT_LPAREN = "TT_LPAREN"
    TT_RPAREN = "TT_RPAREN"
    TT_LSQUARE = "TT_LSQUARE"
    TT_RSQUARE = "TT_RSQUARE"

    TT_DOT = "TT_DOT"
    TT_DOT_2 = "TT_DOT_2"
    TT_DOT_3 = "TT_DOT_3"

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

    TT_PERCENTS = "TT_PERCENTS"
    TT_CARET = "TT_CARET"
    # NODE_TYPES

    NT_TRUE = "NT_TRUE"
    NT_FALSE = "NT_FALSE"
    NT_NIL = "NT_NIL"
    NT_INT = "NT_INT"
    NT_STR = "NT_STR"
    NT_MULTI_STR = "NT_MULTI_STR"
    NT_NAME = "NT_NAME"
    NT_TABLE = "NT_TABLE"
    NT_FUNCTION = "NT_FUNCTION"
    NT_LAMBDA = "NT_LAMBDA"
    NT_BLOCK = "NT_BLOCK"
    NT_LOCAL = "NT_LOCAL"

    NT_IF = "NT_IF"
    NT_NUMERIC_FOR = "NT_NUMERIC_FOR"
    NT_GENERIC_FOR = "NT_GENERIC_FOR"
    NT_WHILE = "NT_WHILE"
    NT_REPEAT = "NT_REPEAT"
    NT_BREAK = "NT_BREAK"
    NT_ASSIGN = "NT_ASSIGN"
    NT_CALL = "NT_CALL"
    NT_DOT = "NT_DOT"
    NT_LOOKUP = "NT_LOOKUP"
    NT_COLON = "NT_COLON"
    NT_COMMA = "NT_COMMA"
    NT_AND = "NT_AND"
    NT_OR = "NT_OR"
    NT_NOT = "NT_NOT"
    # NT_END_EXPR = "NT_END_EXPR"
    # NT_END = "NT_END"

    NT_GT = "NT_GT"
    NT_GE = "NT_GE"
    NT_LE = "NT_LE"
    NT_LT = "NT_LT"
    NT_EQ = "NT_EQ"
    NT_NE = "NT_NE"
    NT_IN = "NT_IN"

    NT_ADD = "NT_ADD"
    NT_SUB = "NT_SUB"
    NT_DIV = "NT_DIV"
    NT_MUL = "NT_MUL"
    NT_POW = "NT_POW"
    NT_MOD = "NT_MOD"
    NT_CONCAT = "NT_CONCAT"

    NT_NEGATE = "NT_NEGATE"

    NT_VARGS = "NT_VARGS"

    RULES = [
        (token('\s'), -1),
        (token('--[^\n]*'), -1),

        (keyword('local'), TT_LOCAL),
        (keyword('do'), TT_DO),
        (keyword('repeat'), TT_REPEAT),
        (keyword('until'), TT_UNTIL),
        (keyword('if'), TT_IF),
        (keyword('then'), TT_THEN),
        (keyword('elseif'), TT_ELSEIF),
        (keyword('else'), TT_ELSE),
        (keyword('end'), TT_END),
        (keyword('and'), TT_AND),
        (keyword('or'), TT_OR),
        (keyword('not'), TT_NOT),
        (keyword('true'), TT_TRUE),
        (keyword('false'), TT_FALSE),
        (keyword('nil'), TT_NIL),

        (keyword('return'), TT_RETURN),
        (keyword('function'), TT_FUNCTION),

        (keyword('while'), TT_WHILE),
        (keyword('for'), TT_FOR),
        (keyword('in'), TT_IN),

        (keyword('break'), TT_BREAK),
        (keyword('continue'), TT_CONTINUE),

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
        (token('\.\.\.'), TT_DOT_3),
        (token('\.\.'), TT_DOT_2),
        (token('\.'), TT_DOT),
        (token(':'), TT_COLON),

        (token('\^'), TT_CARET),
        (token('=='), TT_EQ),
        (token('>='), TT_GE),
        (token('>'), TT_GT),
        (token('<'), TT_LT),
        (token('<='), TT_LE),
        (token('=='), TT_EQ),
        (token('~='), TT_NE),


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
    TERM_FOR_CONDITION = [TT_IN]
    TERM_LOOP_CONDITION = [TT_DO]
    TERM_REPEAT = [TT_UNTIL]
    TERM_IF_BODY = [TT_ELSE, TT_ELSEIF] + TERM_BLOCK
