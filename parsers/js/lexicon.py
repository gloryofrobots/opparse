from opparse.lexicon import Lexicon, token, keyword

name_const = '[a-zA-Z_][0-9a-zA-Z_]*'
typename = '[A-Z][0-9a-zA-Z_]*'
operator_char = '^\s\,\.\@\#\)\(\]\[\}\{\;\w"`\''
operator_const = '[%s]+' % operator_char
backtick_name_const = "`%s`" % name_const
backtick_op_const = "`%s`" % operator_const

decimal_constant = "[0-9]+"
floating_constant = """([0-9]+\.[0-9]+)"""

char_const = "'[^']+'"
string_literal = '"([^\\\"]+|\\.)*"'
multi_string_literal = '"{3}([\s\S]*?"{3})'


class ObinLexicon(Lexicon):
    # TOKEN TYPES

    TT_INT = "TT_INT"
    TT_FLOAT = "TT_FLOAT"
    TT_STR = "TT_STR"
    TT_MULTI_STR = "TT_MULTI_STR"
    TT_CHAR = "TT_CHAR"
    TT_NAME = "TT_NAME"
    TT_OPERATOR = "TT_OPERATOR"
    TT_FUN = "TT_FUN"
    TT_MATCH = "TT_MATCH"
    TT_WITH = "TT_WITH"
    TT_CASE = "TT_CASE"
    TT_FOR = "TT_FOR"
    TT_WHILE = "TT_WHILE"
    TT_IMPLEMENT = "TT_IMPLEMENT"
    TT_EXTEND = "TT_EXTEND"
    TT_DEF = "TT_DEF"
    TT_TYPE = "TT_TYPE"
    TT_IF = "TT_IF"
    TT_ELIF = "TT_ELIF"
    TT_ELSE = "TT_ELSE"
    TT_THEN = "TT_THEN"
    TT_WHEN = "TT_WHEN"
    TT_OF = "TT_OF"
    TT_LET = "TT_LET"
    TT_IN = "TT_IN"
    TT_AS = "TT_AS"
    TT_AND = "TT_AND"
    TT_OR = "TT_OR"
    TT_TRUE = "TT_TRUE"
    TT_FALSE = "TT_FALSE"
    TT_TRY = "TT_TRY"
    TT_THROW = "TT_THROW"
    TT_CATCH = "TT_CATCH"
    TT_FINALLY = "TT_FINALLY"
    TT_IMPORT = "TT_IMPORT"
    TT_FROM = "TT_FROM"
    TT_HIDING = "TT_HIDING"
    TT_HIDE = "TT_HIDE"
    TT_EXPORT = "TT_EXPORT"
    TT_TRAIT = "TT_TRAIT"
    TT_END = "TT_END"
    TT_END_EXPR = "TT_END_EXPR"
    TT_INDENT = "TT_INDENT"
    TT_NEWLINE = "TT_NEWLINE"
    TT_INFIXL = "TT_INFIXL"
    TT_INFIXR = "TT_INFIXR"
    TT_PREFIX = "TT_PREFIX"
    TT_ELLIPSIS = "TT_ELLIPSIS"
    TT_WILDCARD = "TT_WILDCARD"
    TT_ARROW = "TT_ARROW"
    TT_AT_SIGN = "TT_AT_SIGN"
    TT_SHARP = "TT_SHARP"
    TT_LAMBDA = "TT_LAMBDA"
    TT_JUXTAPOSITION = "TT_JUXTAPOSITION"
    TT_LCURLY = "TT_LCURLY"
    TT_RCURLY = "TT_RCURLY"
    TT_COMMA = "TT_COMMA"
    TT_ASSIGN = "TT_ASSIGN"
    TT_INFIX_DOT_LCURLY = "TT_INFIX_DOT_LCURLY"
    TT_INFIX_DOT_LPAREN = "TT_INFIX_DOT_LPAREN"
    TT_INFIX_DOT_LSQUARE = "TT_INFIX_DOT_LSQUARE"
    TT_LPAREN = "TT_LPAREN"
    TT_RPAREN = "TT_RPAREN"
    TT_LSQUARE = "TT_LSQUARE"
    TT_RSQUARE = "TT_RSQUARE"
    TT_DOT = "TT_DOT"
    TT_COLON = "TT_COLON"
    TT_DOUBLE_COLON = "TT_DOUBLE_COLON"
    TT_BACKTICK_NAME = "TT_BACKTICK_NAME"
    TT_BACKTICK_OPERATOR = "TT_BACKTICK_OPERATOR"

    # NODE_TYPES
    NT_TRUE = "NT_TRUE"
    NT_FALSE = "NT_FALSE"
    NT_INT = "NT_INT"
    NT_FLOAT = "NT_FLOAT"
    NT_STR = "NT_STR"
    NT_MULTI_STR = "NT_MULTI_STR"
    NT_CHAR = "NT_CHAR"
    NT_WILDCARD = "NT_WILDCARD"
    NT_NAME = "NT_NAME"
    NT_SYMBOL = "NT_SYMBOL"
    NT_TYPE = "NT_TYPE"
    NT_UNION = "NT_UNION"
    NT_MAP = "NT_MAP"
    NT_LIST = "NT_LIST"
    NT_TUPLE = "NT_TUPLE"
    NT_UNIT = "NT_UNIT"
    NT_CONS = "NT_CONS"
    NT_FUN = "NT_FUN"
    NT_CONDITION = "NT_CONDITION"
    NT_WHEN = "NT_WHEN"
    NT_MATCH = "NT_MATCH"
    NT_TRY = "NT_TRY"
    NT_IMPORT = "NT_IMPORT"
    NT_IMPORT_HIDING = "NT_IMPORT_HIDING"
    NT_IMPORT_FROM = "NT_IMPORT_FROM"
    NT_IMPORT_FROM_HIDING = "NT_IMPORT_FROM_HIDING"
    NT_EXPORT = "NT_EXPORT"
    NT_TRAIT = "NT_TRAIT"
    NT_IMPLEMENT = "NT_IMPLEMENT"
    NT_EXTEND = "NT_EXTEND"
    NT_BIND = "NT_BIND"
    NT_THROW = "NT_THROW"
    NT_REST = "NT_REST"
    NT_ASSIGN = "NT_ASSIGN"
    NT_CALL = "NT_CALL"
    NT_JUXTAPOSITION = "NT_JUXTAPOSITION"
    NT_LOOKUP = "NT_LOOKUP"
    NT_OF = "NT_OF"
    NT_AS = "NT_AS"
    NT_LET = "NT_LET"
    NT_AND = "NT_AND"
    NT_OR = "NT_OR"
    NT_INFIXL = "NT_INFIXL"
    NT_INFIXR = "NT_INFIXR"
    NT_PREFIX = "NT_PREFIX"
    NT_MODIFY = "NT_MODIFY"
    NT_END_EXPR = "NT_END_EXPR"
    NT_END = "NT_END"

    TT_TO_NT_MAPPING = {
        TT_TRUE: NT_TRUE,
        TT_FALSE: NT_FALSE,
        TT_INT: NT_INT,
        TT_FLOAT: NT_FLOAT,
        TT_STR: NT_STR,
        TT_MULTI_STR: NT_MULTI_STR,
        TT_CHAR: NT_CHAR,
        TT_WILDCARD: NT_WILDCARD,
        TT_NAME: NT_NAME,
        TT_IF: NT_CONDITION,
        TT_MATCH: NT_MATCH,
        TT_EXPORT: NT_EXPORT,
        TT_IMPORT: NT_IMPORT,
        TT_TRAIT: NT_TRAIT,
        TT_THROW: NT_THROW,
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
