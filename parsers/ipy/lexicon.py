from opparse.lexicon import Lexicon, token, keyword

name_const = '[a-zA-Z_][0-9a-zA-Z_]*'
decimal_constant = "[0-9]+"
string_literal = '"([^\\\"]+|\\.)*"'
multi_string_literal = '"{3}([\s\S]*?"{3})'


class ObinLexicon(Lexicon):
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
    TT_THEN = "TT_THEN"
    TT_IN = "TT_IN"
    TT_AS = "TT_AS"
    TT_AND = "TT_AND"
    TT_OR = "TT_OR"
    TT_TRUE = "TT_TRUE"
    TT_FALSE = "TT_FALSE"
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
    TT_LPAREN = "TT_LPAREN"
    TT_RPAREN = "TT_RPAREN"
    TT_LSQUARE = "TT_LSQUARE"
    TT_RSQUARE = "TT_RSQUARE"
    TT_DOT = "TT_DOT"
    TT_COLON = "TT_COLON"
    TT_PLUS = "TT_PLUS"
    TT_DASH = "TT_DASH"
    TT_SLASH = "TT_SLASH"
    TT_STAR = "TT_STAR"
    TT_DOUBLE_STAR = "TT_DOUBLE_STAR"

    # NODE_TYPES
    NT_TRUE = "NT_TRUE"
    NT_FALSE = "NT_FALSE"
    NT_INT = "NT_INT"
    NT_STR = "NT_STR"
    NT_MULTI_STR = "NT_MULTI_STR"
    NT_NAME = "NT_NAME"
    NT_DICT = "NT_DICT"
    NT_LIST = "NT_LIST"
    NT_TUPLE = "NT_TUPLE"
    NT_FUN = "NT_FUN"
    NT_CONDITION = "NT_CONDITION"
    NT_TRY = "NT_TRY"
    NT_RAISE = "NT_RAISE"
    NT_ASSIGN = "NT_ASSIGN"
    NT_CALL = "NT_CALL"
    NT_LOOKUP = "NT_LOOKUP"
    NT_AS = "NT_AS"
    NT_AND = "NT_AND"
    NT_OR = "NT_OR"
    NT_END_EXPR = "NT_END_EXPR"
    NT_END = "NT_END"

    TT_PLUS = "TT_PLUS"
    TT_DASH = "TT_DASH"
    TT_SLASH = "TT_SLASH"
    TT_STAR = "TT_STAR"
    TT_DOUBLE_STAR = "TT_DOUBLE_STAR"

    TT_TO_NT_MAPPING = {
        TT_TRUE: NT_TRUE,
        TT_FALSE: NT_FALSE,
        TT_INT: NT_INT,
        TT_STR: NT_STR,
        TT_CHAR: NT_CHAR,
        TT_WILDCARD: NT_WILDCARD,
        TT_NAME: NT_NAME,
        TT_RAISE: NT_RAISE,
        TT_ELLIPSIS: NT_REST,
        TT_ASSIGN: NT_ASSIGN,
        TT_OF: NT_OF,
        TT_AS: NT_AS,
        TT_AND: NT_AND,
        TT_OR: NT_OR,
        TT_SHARP: NT_SYMBOL,
        TT_OPERATOR: NT_NAME,
        TT_DOUBLE_COLON: NT_CONS,
        TT_DOT: NT_LOOKUP,
    }

    RULES = [
        (token('\n'), TT_NEWLINE),
        (token('[ ]*\.\.\.'), TT_ELLIPSIS),
        (token('\.\{'), TT_INFIX_DOT_LCURLY),
        (token('\.\('), TT_INFIX_DOT_LPAREN),
        (token('\.\['), TT_INFIX_DOT_LSQUARE),
        (token(' '), -1),
        (token('//[^\n]*'), -1),
        (token('/\*[^\*\/]*\*/'), -1),

        (keyword('if'), TT_IF),
        (keyword('elif'), TT_ELIF),
        (keyword('else'), TT_ELSE),

        (keyword('then'), TT_THEN),
        (keyword('of'), TT_OF),
        (keyword('match'), TT_MATCH),
        (keyword('with'), TT_WITH),
        (keyword('fun'), TT_FUN),
        (keyword('end'), TT_END),
        (keyword('and'), TT_AND),
        (keyword('or'), TT_OR),
        (keyword('True'), TT_TRUE),
        (keyword('False'), TT_FALSE),
        # (keyword('nil'), TT_NIL),
        (keyword('throw'), TT_THROW),
        (keyword('try'), TT_TRY),
        (keyword('catch'), TT_CATCH),
        (keyword('finally'), TT_FINALLY),
        (keyword('lam'), TT_LAMBDA),
        # (keyword('module'), TT_MODULE),

        (keyword('trait'), TT_TRAIT),
        (keyword('implement'), TT_IMPLEMENT),
        (keyword('extend'), TT_EXTEND),
        (keyword('def'), TT_DEF),
        (keyword('type'), TT_TYPE),
        (keyword('for'), TT_FOR),

        (keyword('export'), TT_EXPORT),
        (keyword('import'), TT_IMPORT),
        (keyword('from'), TT_FROM),
        (keyword('hiding'), TT_HIDING),
        (keyword('hide'), TT_HIDE),

        (keyword('of'), TT_OF),
        (keyword('as'), TT_AS),
        (keyword('let'), TT_LET),
        (keyword('when'), TT_WHEN),

        (keyword('in'), TT_IN),

        (keyword('infixl'), TT_INFIXL),
        (keyword('infixr'), TT_INFIXR),
        (keyword('prefix'), TT_PREFIX),

        (keyword('_'), TT_WILDCARD),

        # **********

        (token(floating_constant), TT_FLOAT),
        (token(decimal_constant), TT_INT),
        (token(multi_string_literal), TT_MULTI_STR),
        (token(string_literal), TT_STR),
        (token(char_const), TT_CHAR),
        (token(backtick_name_const), TT_BACKTICK_NAME),
        (token(backtick_op_const), TT_BACKTICK_OPERATOR),
        # (typename, TT_TYPENAME),
        (token(name_const), TT_NAME),

        (token('\-\>'), TT_ARROW),
        # (token('\<\-'), TT_BACKARROW),
        (token('\;'), TT_END_EXPR),
        (token('#'), TT_SHARP),
        (token('\{'), TT_LCURLY),
        (token('\}'), TT_RCURLY),
        (token('\,'), TT_COMMA),
        (token('\('), TT_LPAREN),
        (token('\)'), TT_RPAREN),
        (token('\['), TT_LSQUARE),
        (token('\]'), TT_RSQUARE),
        (token('\.'), TT_DOT),
        (token('@'), TT_AT_SIGN),
        (token('::'), TT_DOUBLE_COLON),
        (token('[:^:][%s]+' % operator_char), TT_OPERATOR),
        (token(':'), TT_COLON),
        (token('[%s][=]+' % operator_char), TT_OPERATOR),
        (token('[=][%s]+' % operator_char), TT_OPERATOR),
        (token('[%s][|]+' % operator_char), TT_OPERATOR),
        (token('[|][%s]+' % operator_char), TT_OPERATOR),
        # (token('[%s][:]+' % operator_char), TT_OPERATOR),
        # (token('[:][%s]+' % operator_char), TT_OPERATOR),

        (token('\|'), TT_CASE),
        (token('='), TT_ASSIGN),

        # that can catch op
        (token(operator_const), TT_OPERATOR),
    ]

    TERM_BLOCK = [TT_END]
    TERM_EXP = [TT_END_EXPR]

    TERM_IF_BODY = [TT_ELSE, TT_ELIF]
    TERM_IF_CONDITION = [TT_THEN]

    TERM_MATCH_EXPR = [TT_WITH]
    TERM_MATCH_PATTERN = [TT_WITH]
    TERM_CASE = [TT_CASE] + TERM_BLOCK
    # TERM_CATCH = [TT_CATCH, TT_FINALLY] + TERM_BLOCK
    TERM_TRY = [TT_CATCH, TT_FINALLY]
    TERM_CATCH_CASE = [TT_CASE, TT_FINALLY] + TERM_BLOCK
    TERM_SINGLE_CATCH = [TT_FINALLY] + TERM_BLOCK

    TERM_LET = [TT_IN]

    TERM_PATTERN = [TT_WHEN]
    TERM_FUN_GUARD = [TT_ARROW]
    TERM_FUN_PATTERN = [TT_WHEN, TT_ARROW]
    TERM_FUN_SIGNATURE = [TT_ARROW, TT_CASE]

    TERM_CONDITION_BODY = [TT_CASE] + TERM_BLOCK
    TERM_BEFORE_FOR = [TT_FOR]

    TERM_BEFORE_WITH = [TT_WITH]

    TERM_TYPE_ARGS = TERM_BLOCK
    TERM_UNION_TYPE_ARGS = [TT_CASE] + TERM_BLOCK

    TERM_METHOD_SIG = [TT_DEF, TT_ARROW] + TERM_BLOCK
    TERM_METHOD_DEFAULT_BODY = [TT_DEF] + TERM_BLOCK
    TERM_METHOD_CONSTRAINTS = [TT_DEF] + TERM_BLOCK
    TERM_IMPL_BODY = [TT_CASE, TT_DEF] + TERM_BLOCK
    TERM_IMPL_HEADER = [TT_DEF] + TERM_BLOCK

    TERM_EXTEND_TRAIT = [TT_DEF, TT_ASSIGN] + TERM_BLOCK
    TERM_EXTEND_MIXIN_TRAIT = [TT_WITH] + TERM_BLOCK

    TERM_EXTEND_BODY = [TT_CASE, TT_DEF, TT_WITH] + TERM_BLOCK

    TERM_FROM_IMPORTED = [TT_IMPORT, TT_HIDE]

    TERM_CONDITION_CONDITION = [TT_ARROW]

    NODE_IMPLEMENT_NAME = [NT_NAME, NT_LOOKUP]

    LEVELS_MATCH = TERM_MATCH_EXPR
    LEVELS_IF = [TT_ELSE, TT_ELIF]
    LEVELS_TRY = [TT_CATCH, TT_FINALLY]
    LEVELS_LET = [TT_IN]

