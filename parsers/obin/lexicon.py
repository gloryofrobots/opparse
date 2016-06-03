from opparse.parse.lexicon import Lexicon, token, keyword

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
    TT_INT = 1
    TT_FLOAT = 2
    TT_STR = 3
    TT_MULTI_STR = 4
    TT_CHAR = 5
    TT_NAME = 6
    TT_TYPENAME = 7
    TT_OPERATOR = 8
    TT_FUN = 9
    TT_MATCH = 10
    TT_WITH = 11
    TT_CASE = 12
    TT_BREAK = 13
    TT_CONTINUE = 14
    TT_FOR = 15
    TT_WHILE = 16
    TT_IMPLEMENT = 17
    TT_EXTEND = 18
    TT_DEF = 19
    TT_TYPE = 20
    TT_IF = 21
    TT_ELIF = 22
    TT_ELSE = 23
    TT_THEN = 24
    TT_WHEN = 25
    TT_OF = 26
    TT_LET = 27
    TT_IN = 28
    TT_AS = 29
    TT_DELAY = 30
    TT_AND = 31
    TT_OR = 32
    TT_TRUE = 33
    TT_FALSE = 34
    TT_TRY = 35
    TT_ENSURE = 36
    TT_THROW = 37
    TT_CATCH = 38
    TT_FINALLY = 39
    TT_MODULE = 40
    TT_IMPORT = 41
    TT_FROM = 42
    TT_HIDING = 43
    TT_HIDE = 44
    TT_EXPORT = 45
    TT_TRAIT = 46
    TT_END = 47
    TT_END_EXPR = 48
    TT_INDENT = 49
    TT_NEWLINE = 50
    TT_INFIXL = 51
    TT_INFIXR = 52
    TT_PREFIX = 53
    TT_ELLIPSIS = 54
    TT_WILDCARD = 55
    TT_GOTO = 56
    TT_ARROW = 57
    TT_BACKARROW = 58
    TT_AT_SIGN = 59
    TT_SHARP = 60
    TT_LAMBDA = 61
    TT_JUXTAPOSITION = 62
    TT_SPACE_DOT = 63
    TT_LCURLY = 64
    TT_RCURLY = 65
    TT_COMMA = 66
    TT_ASSIGN = 67
    TT_INFIX_DOT_LCURLY = 68
    TT_INFIX_DOT_LPAREN = 69
    TT_INFIX_DOT_LSQUARE = 70
    TT_LPAREN = 71
    TT_RPAREN = 72
    TT_LSQUARE = 73
    TT_RSQUARE = 74
    TT_DOT = 75
    TT_COLON = 76
    TT_DOUBLE_COLON = 77
    TT_TRIPLE_COLON = 78
    TT_DOUBLE_DOT = 79
    TT_BACKTICK_NAME = 80
    TT_BACKTICK_OPERATOR = 81

    NT_GOTO = 0
    NT_TRUE = 1
    NT_FALSE = 2
    NT_VOID = 3
    NT_INT = 4
    NT_FLOAT = 5
    NT_STR = 6
    NT_MULTI_STR = 7
    NT_CHAR = 8
    NT_WILDCARD = 9
    NT_NAME = 10
    NT_TEMPORARY = 11
    NT_SYMBOL = 12
    NT_TYPE = 13
    NT_UNION = 14
    NT_MAP = 15
    NT_LIST = 16
    NT_TUPLE = 17
    NT_UNIT = 18
    NT_CONS = 19
    NT_COMMA = 20
    NT_CASE = 21
    NT_FUN = 22
    NT_FENV = 23
    NT_CONDITION = 24
    NT_WHEN = 25
    NT_MATCH = 26
    NT_TRY = 27
    NT_MODULE = 28
    NT_IMPORT = 29
    NT_IMPORT_HIDING = 30
    NT_IMPORT_FROM = 31
    NT_IMPORT_FROM_HIDING = 32
    NT_EXPORT = 33
    NT_LOAD = 34
    NT_TRAIT = 35
    NT_IMPLEMENT = 36
    NT_EXTEND = 37
    NT_BIND = 38
    NT_THROW = 39
    NT_REST = 40
    NT_ASSIGN = 41
    NT_CALL = 42
    NT_JUXTAPOSITION = 43
    NT_UNDEFINE = 44
    NT_LOOKUP = 45
    NT_IMPORTED_NAME = 46
    NT_HEAD = 47
    NT_TAIL = 48
    NT_DROP = 49
    NT_RANGE = 50
    NT_MODIFY = 51
    NT_OF = 52
    NT_AS = 53
    NT_DELAY = 54
    NT_LET = 55
    NT_AND = 56
    NT_OR = 57
    NT_END_EXPR = 58
    NT_END = 59

    TT_TO_NT_MAPPING = {
        TT_COLON: NT_IMPORTED_NAME,
        TT_TRUE: NT_TRUE,
        TT_FALSE: NT_FALSE,
        TT_INT: NT_INT,
        TT_FLOAT: NT_FLOAT,
        TT_STR: NT_STR,
        TT_MULTI_STR: NT_MULTI_STR,
        TT_CHAR: NT_CHAR,
        TT_WILDCARD: NT_WILDCARD,
        TT_NAME: NT_NAME,
        TT_TYPENAME: NT_NAME,
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
        TT_DOUBLE_DOT: NT_RANGE,
        TT_SHARP: NT_SYMBOL,
        TT_OPERATOR: NT_NAME,
        TT_DOUBLE_COLON: NT_CONS,
        TT_CASE: NT_CASE,
    }

    RULES = [
        (token('\n'), TT_NEWLINE),
        (token('[ ]*\.\.\.'), TT_ELLIPSIS),
        (token(' \.'), TT_SPACE_DOT),
        (token('\.\{'), TT_INFIX_DOT_LCURLY),
        (token('\.\('), TT_INFIX_DOT_LPAREN),
        (token('\.\['), TT_INFIX_DOT_LSQUARE),
        (token(' '), -1),
        (token('-----[-]*'), -1),
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
        (keyword('ensure'), TT_ENSURE),
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

        (keyword('delay'), TT_DELAY),
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
        (token('\.\.'), TT_DOUBLE_DOT),
        (token('@'), TT_AT_SIGN),
        (token(':::'), TT_TRIPLE_COLON),
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
