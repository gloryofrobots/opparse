__author__ = 'gloryofrobots'
from opparse.parse.tokenstream import TokenStream
from opparse.parse.indenter import IndentationTokenStream, InvalidIndentationError
from opparse.parse.callbacks import *
from opparse.parse.lexer import UnknownTokenError
from opparse.parse import tokens
import opparse.parse.lexer as lexer


# additional helpers
def infix_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infix_function, infix_function)


def infixr_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infixr_function, infix_function)


def prefix_operator(parser, ttype, prefix_function):
    op = get_or_create_operator(parser, ttype)
    operator_prefix(op, prefix_nud_function, prefix_function)


def infixr(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr)


def assignment(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr_assign)


class Parser:

    def __init__(self, settings):
        self.handlers = {}
        self.state = None
        self.allow_overloading = settings.get("allow_overloading", False)
        self.break_on_juxtaposition = settings.get(
            "break_on_juxtaposition", False)

        self.allow_unknown = settings.get("allow_unknown", True)

        self.juxtaposition_as_list = settings.get(
            "juxtaposition_as_list", True)

        self.subparsers = {}

    def add_subparser(parser_name, parser):
        setattr(self, parser_name, parser)
        self.subparsers[parser_name] = parser

    def open(self, state):
        assert self.state is None
        self.state = state
        for parser in self.subparsers.values():
            parser._on_open(state)

        self._on_open(state)

    def _on_open(self, state):
        pass

    def close(self):
        state = self.state
        self.state = None
        for parser in self.subparsers.values():
            parser._on_close(state)

        self._on_close()
        return state

    def _on_close(self):
        pass

    @property
    def ts(self):
        return self.state.ts

    @property
    def token_type(self):
        return tokens.token_type(self.ts.token)

    # @property
    # def is_newline_occurred(self):
    #     return self.ts.is_newline_occurred

    @property
    def node(self):
        return self.ts.node

    @property
    def token(self):
        return self.ts.token

    def next_token(self):
        try:
            return self.ts.next_token()
        except InvalidIndentationError as e:
            parser_error_indentation(self, e.msg, e.position, e.line, e.column)
        except UnknownTokenError as e:
            parser_error_unknown(self, e.position)

    def isend(self):
        return self.token_type == TT_ENDSTREAM


def newparser():
    parser = ModuleParser()
    return parser


def newtokenstream():
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return IndentationTokenStream(tokens_iter, source)


def parse(src):
    parser = ModuleParser()
    ts = newtokenstream(src)
    parser.open(ParseState(ts))

    parser.next_token()
    stmts, scope = parse_module(parser, TERM_FILE)
    assert plist.is_empty(parser.state.scopes)
    check_token_type(parser, TT_ENDSTREAM)
    parser.close()
    return stmts, scope
