from opparse.parse.basic import *
from opparse.parse.node_type import *
from opparse.parse import nodes, tokens
from opparse.parse.nodes import (
    node_token as __ntok, node_0, node_1, node_2, node_3, list_node, empty_node)
from opparse.misc import strutil
from opparse.parse.parser import newparser
from callbacks import *

""" GOLANG PRECEDENCES. SOURCE OF INSPIRATION
Precedence    Operator
    5             *  /  %  <<  >>  &  &^
    4             +  -  |  ^
    3             ==  !=  <  <=  >  >=
    2             &&
    1             ||
"""
"""
OPPARSE PRECEDENCES
Precedence    Operator
    100           : . .{ .(
    95           JUXTAPOSITION
    60           :: :::
    50           *  /
    40           +  - ++
    35           ==  !=  <  <=  >  >=
    30           and
    25           or << >>
    20           |>
    15           " ."  as of <|
    10           = := @
"""

from opparse.parse.indenter import IndentationTokenStream, InvalidIndentationError

def newtokenstream(source):
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return IndentationTokenStream(tokens_iter, source)

def create_parser():
    indenter_settings = dict(
        operator_tokens=[tt.TT_SPACE_DOT, tt.TT_DOUBLE_COLON,
                         tt.TT_TRIPLE_COLON,
                         tt.TT_COLON, tt.TT_OPERATOR,
                         tt.TT_DOT, tt.TT_ASSIGN, tt.TT_OR, tt.TT_AND],

        end_token=tt.TT_END,
        end_stream_token=tt.TT_ENDSTREAM,
        new_line_token=tt.TT_NEWLINE
    )



class ModuleParser(BaseParser):

    def __init__(self, proc_data):
        BaseParser.__init__(self)

        self.import_parser = import_parser_init(BaseParser())

        self.pattern_parser = pattern_parser_init(BaseParser())
        self.guard_parser = guard_parser_init(proc_data, BaseParser())

        self.fun_pattern_parser = fun_pattern_parser_init(BaseParser())
        self.fun_signature_parser = fun_signature_parser_init(BaseParser())

        self.expression_parser = ExpressionParser(proc_data)
        self.name_parser = name_parser_init(BaseParser())
        self.import_names_parser = import_names_parser_init(BaseParser())
        self.type_parser = type_parser_init(BaseParser())
        self.method_signature_parser = method_signature_parser_init(
            BaseParser())

        module_parser_init(self)

    def on_endofexpression(self):
        if self.isend():
            return None
        if self.token_type in TERM_BLOCK:
            return parser.node
        if self.token_type == self.lex.TT_END_EXPR:
            return advance(parser)
        return False

    def _on_open(self, state):
        self.method_signature_parser.open(state)
        self.type_parser.open(state)

        self.pattern_parser.open(state)
        self.guard_parser.open(state)
        self.fun_pattern_parser.open(state)
        self.fun_signature_parser.open(state)

        self.import_parser.open(state)
        self.expression_parser.open(state)
        self.name_parser.open(state)
        self.import_names_parser.open(state)

    def _on_close(self):
        self.method_signature_parser.close()
        self.type_parser.close()
        self.pattern_parser.close()
        self.fun_pattern_parser.close()
        self.fun_signature_parser.close()
        self.guard_parser.close()
        self.import_parser.close()
        self.expression_parser.close()
        self.name_parser.close()
        self.import_names_parser.close()


def name_parser_init(parser):
    parser.break_on_juxtaposition = True
    parser.allow_unknown = True
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_UNKNOWN, None)
    # symbol(parser, TT_WILDCARD, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_INDENT, None)
    init_parser_literals(parser)
    symbol(parser, TT_CASE, None)
    symbol(parser, TT_ASSIGN, None)
    symbol(parser, TT_ELLIPSIS, None)
    symbol(parser, TT_ENDSTREAM)

    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    symbol(parser, TT_OPERATOR, symbol_operator_name)
    infix(parser, TT_COLON, 100, infix_name_pair)
    return parser


def type_parser_init(parser):
    # parser.break_on_juxtaposition = True
    parser.juxtaposition_as_list = True
    parser.allow_unknown = True
    symbol(parser, TT_UNKNOWN)
    # literal(parser, TT_TYPENAME)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_END)
    symbol(parser, TT_RCURLY)
    prefix(parser, TT_LCURLY, prefix_lcurly_type, layout_lcurly)
    prefix(parser, TT_NAME, prefix_name_as_symbol)
    infix(parser, TT_COLON, 100, infix_name_pair)
    # infix(parser, TT_CASE, 15, led_infixr)
    # infix(parser, TT_ASSIGN, 10, led_infixr)
    infix(parser, TT_JUXTAPOSITION, 5, infix_juxtaposition)
    infix(parser, TT_SPACE_DOT, 5, infix_juxtaposition)
    symbol(parser, TT_CASE, None)
    return parser


def method_signature_parser_init(parser):
    parser.juxtaposition_as_list = True
    prefix(parser, TT_NAME, prefix_name_as_symbol)
    symbol(parser, TT_DEF, None)
    symbol(parser, TT_END, None)
    symbol(parser, TT_ARROW, None)
    infix(parser, TT_JUXTAPOSITION, 5, infix_juxtaposition)
    infix(parser, TT_SPACE_DOT, 5, infix_juxtaposition)
    return parser


def import_names_parser_init(parser):
    parser.allow_unknown = True
    symbol(parser, TT_UNKNOWN)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    literal(parser, TT_NAME)
    infix(parser, TT_AS, 15, infix_name_pair)
    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    return parser


def import_parser_init(parser):
    parser.allow_unknown = True
    symbol(parser, TT_UNKNOWN)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_LPAREN, None)
    symbol(parser, TT_HIDING, None)
    symbol(parser, TT_HIDE, None)
    symbol(parser, TT_IMPORT, None)
    symbol(parser, TT_WILDCARD, None)
    infix(parser, TT_COLON, 100, infix_name_pair)
    infix(parser, TT_AS, 15, infix_name_pair)
    literal(parser, TT_NAME)

    return parser


def guard_parser_init(proc_data, parser):
    parser.allow_overloading = True
    parser = init_parser_literals(parser)

    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ARROW, None)

    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_BACKTICK_OPERATOR, prefix_backtick_operator)

    infix(parser, TT_SPACE_DOT, 15, infix_spacedot)

    infix(parser, TT_OR, 25, led_infix)
    infix(parser, TT_AND, 30, led_infix)
    infix(parser, TT_BACKTICK_NAME, 35, infix_backtick_name)
    infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, TT_DOT, 100, infix_dot)
    infix(parser, TT_COLON, 100, infix_name_pair)
    return parser


def pattern_parser_init(parser):
    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly_patterns, layout_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_ELLIPSIS, prefix_nud)

    infix(parser, TT_OF, 10, led_infix)
    infix(parser, TT_AT_SIGN, 10, infix_at)
    infix(parser, TT_DOUBLE_COLON, 60, led_infixr)
    infix(parser, TT_COLON, 100, infix_name_pair)

    symbol(parser, TT_WHEN)
    symbol(parser, TT_CASE)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_ASSIGN)

    parser = init_parser_literals(parser)
    return parser


def fun_pattern_parser_init(parser):
    parser = pattern_parser_init(parser)
    parser.break_on_juxtaposition = False
    parser.juxtaposition_as_list = True
    infix(parser, TT_JUXTAPOSITION, 5, infix_juxtaposition)
    infix(parser, TT_SPACE_DOT, 5, infix_juxtaposition)
    return parser


def fun_signature_parser_init(parser):
    parser.juxtaposition_as_list = True
    literal(parser, TT_NAME)

    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_INDENT)
    prefix(parser, TT_ELLIPSIS, prefix_nud)

    infix(parser, TT_OF, 15, led_infix)
    infix(parser, TT_COLON, 100, infix_name_pair)

    literal(parser, TT_WILDCARD)
    symbol(parser, TT_DEF)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_CASE)
    infix(parser, TT_JUXTAPOSITION, 5, infix_juxtaposition)
    infix(parser, TT_SPACE_DOT, 5, infix_juxtaposition)
    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_MULTI_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_TYPENAME)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_WILDCARD)
    return parser


def expression_parser_init(proc_data, parser):
    parser.allow_overloading = True

    parser = init_parser_literals(parser)

    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_THEN)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_END_EXPR)
    symbol(parser, TT_AT_SIGN)
    symbol(parser, TT_ELSE)
    symbol(parser, TT_ELIF)
    symbol(parser, TT_CASE)
    symbol(parser, TT_THEN)
    symbol(parser, TT_CATCH)
    symbol(parser, TT_FINALLY)
    symbol(parser, TT_WITH)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_END)
    symbol(parser, TT_IN)

    prefix(parser, TT_INDENT, prefix_indent)
    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_FUN, prefix_fun)
    prefix(parser, TT_LAMBDA, prefix_lambda)

    prefix(parser, TT_MATCH, prefix_match)
    prefix(parser, TT_TRY, prefix_try)
    prefix(parser, TT_BACKTICK_OPERATOR, prefix_backtick_operator)
    prefix(parser, TT_DELAY, prefix_delay)
    prefix(parser, TT_LET, prefix_let)

    assignment(parser, TT_ASSIGN, 10)
    infix(parser, TT_SPACE_DOT, 15, infix_spacedot)
    infix(parser, TT_OF, 15, led_infix)
    infix(parser, TT_OR, 25, led_infix)
    infix(parser, TT_AND, 30, led_infix)
    infix(parser, TT_BACKTICK_NAME, 35, infix_backtick_name)
    infix(parser, TT_DOUBLE_COLON, 70, led_infixr)
    infix(parser, TT_TRIPLE_COLON, 70, infix_triple_colon)

    infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, TT_COLON, 100, infix_name_pair)
    infix(parser, TT_DOT, 100, infix_dot)

    infix(parser, TT_INFIX_DOT_LCURLY, 100, infix_lcurly)
    infix(parser, TT_INFIX_DOT_LSQUARE, 100, infix_lsquare)

    # OTHER OPERATORS ARE DECLARED IN prelude.obn

    stmt(parser, TT_THROW, prefix_throw)
    return parser


def module_parser_init(parser):
    parser = init_parser_literals(parser)
    parser.allow_overloading = True

    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_END)
    symbol(parser, TT_END_EXPR)
    symbol(parser, TT_ENDSTREAM)

    prefix(parser, TT_INDENT, prefix_indent)
    prefix(parser, TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_LAMBDA, prefix_lambda)

    assignment(parser, TT_ASSIGN, 10)
    infix(parser, TT_SPACE_DOT, 15, infix_spacedot)
    infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, TT_DOT, 100, infix_dot)
    infix(parser, TT_COLON, 100, infix_name_pair)

    stmt(parser, TT_FUN, prefix_module_fun)
    stmt(parser, TT_TRAIT, stmt_trait)
    stmt(parser, TT_TYPE, stmt_type)
    stmt(parser, TT_IMPLEMENT, stmt_implement)
    stmt(parser, TT_EXTEND, stmt_extend)
    stmt(parser, TT_IMPORT, stmt_import)
    stmt(parser, TT_FROM, stmt_from)
    stmt(parser, TT_EXPORT, stmt_export)
    # stmt(parser, TT_MODULE, stmt_module)
    stmt(parser, TT_INFIXL, stmt_infixl)
    stmt(parser, TT_INFIXR, stmt_infixr)
    stmt(parser, TT_PREFIX, stmt_prefix)
    return parser
