import operator

from opparse import nodes, lexer
from opparse.misc.strutil import get_line, get_line_for_position
from opparse.indenter import InvalidIndentationError


class ParseError(RuntimeError):
    pass


def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    raise ParseError([
        position,
        "Unknown Token",
        line
    ])


def parser_error_indentation(parser, msg, position, lineno, column):
    print parser.ts.advanced_values()
    print parser.ts.layouts
    line = get_line_for_position(parser.ts.src, position)
    raise ParseError([
        position,
        lineno,
        column,
        msg,
        line
    ])


def parse_error(parser, message, node):
    print parser.ts.advanced_values()
    print parser.ts.layouts
    if node.token_type == parser.lex.TT_ENDSTREAM:
        line = "Unclosed top level statement"
    else:
        line = get_line(parser.ts.src, node.token_line)

    raise ParseError([
        node.token_position,
        node.token_line,
        node.token_column,
        str(node),
        message,
        line
    ])


def init_code_layout(parser, node, terminators=None):
    skip_indent(parser)
    parser.ts.add_code_layout(node, terminators)


def init_offside_layout(parser, node):
    parser.ts.add_offside_layout(node)


def init_node_layout(parser, node, level_tokens=None):
    parser.ts.add_node_layout(node, level_tokens)


def init_free_layout(parser, node, terminators):
    skip_indent(parser)
    parser.ts.add_free_code_layout(node, terminators)


def skip_indent(parser):
    if parser.token_type == parser.lex.TT_INDENT:
        advance(parser)


class Operator(object):

    def __init__(self):
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1
        # self.is_breaker = False
        self.layout = None

        self.prefix_function = None
        self.infix_function = None

    def __hash__(self):
        _hash = 0
        if self.prefix_function:
            _hash += hash(self.prefix_function)
        if self.infix_function:
            _hash += hash(self.infix_function)
        return _hash

    def prefix_s(self):
        return "'%s'" % self.prefix_function if self.prefix_function else ""

    def infix_s(self):
        return "'%s'" % self.infix_function if self.infix_function else ""

    def _equal_(self, other):
        if not isinstance(other, Operator):
            return False
        if self.nud != other.nud or self.led != other.led \
                or self.std != other.std and self.lbp != other.lbp:
            return False

        if self.prefix_function and other.prefix_function:
            if not operator.eq(self.prefix_function, other.prefix_function):
                return False
        elif self.prefix_function or other.prefix_function:
            return False

        if self.infix_function and other.infix_function:
            if not operator.eq(self.infix_function, other.infix_function):
                return False
        elif self.infix_function or other.infix_function:
            return False

        return True

    def __str__(self):
        return 'Operator(%s %s)' % (self.prefix_s(), self.infix_s())


class ParserScope(object):

    def __init__(self):
        self.custom_operators = {}
        self.macro = {}

    def has_custom_operator(self, op_name):
        return op_name in self.custom_operators

    def new_custom_operator(self, op_name):
        op = Operator()
        self.custom_operators[op_name] = op
        return op

    def get_custom_operator(self, op_name):
        op = self.custom_operators[op_name]
        return op

    def get_custom_operator_or_create_new(self, op_name):
        if self.has_custom_operator(op_name):
            op = self.get_custom_operator(op_name)
        else:
            op = self.new_custom_operator(op_name)

        return op



class ParseState:

    def __init__(self, ts):
        self.ts = ts
        self.scopes = []


class Parser:

    def __init__(self, lexicon, allow_overloading=False,
                 break_on_juxtaposition=False, allow_unknown=True,
                 juxtaposition_as_list=False):

        self.lex = lexicon
        self.operators = {}
        self.state = None
        self.allow_overloading = allow_overloading
        self.break_on_juxtaposition = break_on_juxtaposition
        self.allow_unknown = allow_unknown
        self.juxtaposition_as_list = juxtaposition_as_list

        self.subparsers = {}

    def on_endofexpression(self):
        raise NotImplementedError()

    def add_subparser(self, parser_name, parser):
        setattr(self, parser_name, parser)
        self.subparsers[parser_name] = parser

    def open(self, state):
        assert self.state is None
        self.state = state
        for parser in self.subparsers.values():
            parser.open(state)

    def close(self):
        state = self.state
        self.state = None
        for parser in self.subparsers.values():
            parser.close()

        return state

    @property
    def ts(self):
        return self.state.ts

    @property
    def token_type(self):
        return self.ts.token.type

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
        except lexer.UnknownTokenError as e:
            parser_error_unknown(self, e.position)

    def isend(self):
        return self.token_type == self.lex.TT_ENDSTREAM

    def enter_scope(self):
        self.state.scopes.append(ParserScope())

    def exit_scope(self):
        return self.state.scopes.pop()

    def current_scope(self):
        return self.state.scopes[-1]

    def find_custom_operator(self, op_name):
        scopes = self.state.scopes
        for scope in scopes:
            op = scope.custom_operators.get(op_name, None)
            if op is not None:
                return op

        return None


def parser_has_operator(parser, ttype):
    return ttype in parser.operators


def parser_operator(parser, ttype):
    try:
        return parser.operators[ttype]
    except:
        if ttype == parser.lex.TT_UNKNOWN:
            return parse_error(parser, "Invalid token", parser.node)

        if parser.allow_unknown is True:
            return parser_operator(parser, parser.lex.TT_UNKNOWN)
        return parse_error(parser,
                           "Invalid token %s" % ttype,
                           parser.node)


def get_or_create_operator(parser, ttype):
    if not parser_has_operator(parser, ttype):
        return parser_set_operator(parser, ttype, Operator())
    return parser_operator(parser, ttype)


def parser_set_operator(parser, ttype, h):
    parser.operators[ttype] = h
    return parser_operator(parser, ttype)


def node_operator(parser, node):
    ttype = node.token_type
    if not parser.allow_overloading:
        return parser_operator(parser, ttype)

    if ttype != parser.lex.TT_OPERATOR:
        return parser_operator(parser, ttype)

    # in case of operator
    op = parser.find_custom_operator(node.token_value)
    if op is None:
        return parse_error(parser, "Invalid operator", node)
    return op


def node_nud(parser, node):
    handler = node_operator(parser, node)
    if not handler.nud:
        parse_error(parser, "Unknown token nud", node)
    return handler.nud(parser, handler, node)


def node_std(parser, node):
    handler = node_operator(parser, node)
    if not handler.std:
        parse_error(parser, "Unknown token std", node)

    return handler.std(parser, handler, node)


def node_has_nud(parser, node):
    handler = node_operator(parser, node)
    return handler.nud is not None


def node_has_layout(parser, node):
    handler = node_operator(parser, node)
    return handler.layout is not None


def node_has_led(parser, node):
    handler = node_operator(parser, node)
    return handler.led is not None


def node_has_std(parser, node):
    handler = node_operator(parser, node)
    return handler.std is not None


def node_lbp(parser, node):
    handler = node_operator(parser, node)
    lbp = handler.lbp
    # if lbp < 0:
    #   parse_error(parser, "Left binding power error", node)

    return lbp


def node_led(parser, node, left):
    handler = node_operator(parser, node)
    if not handler.led:
        parse_error(parser, "Unknown token led", node)

    return handler.led(parser, handler, node, left)


def node_layout(parser, node):
    handler = node_operator(parser, node)
    if not handler.layout:
        parse_error(parser, "Unknown token layout", node)

    return handler.layout(parser, handler, node)


def token_is_one_of(parser, types):
    return parser.token_type in types


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser,
                    "Wrong token type, expected %s, got %s" %
                    (type, parser.token_type),
                    parser.node)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, "Wrong token type, expected one of %s, got %s" %
                    (unicode([type for type in types]),
                     parser.token_type), parser.node)


def check_list_node_types(parser, node, expected_types):
    for child in node:
        check_node_types(parser, child, expected_types)


def check_node_type(parser, node, expected_type):
    ntype = node.node_type
    if ntype != expected_type:
        parse_error(parser, "Wrong node type, expected  %s, got %s" %
                    (expected_type, ntype), node)


def check_node_types(parser, node, types):
    ntype = node.node_type
    if ntype not in types:
        parse_error(parser, "Wrong node type, expected one of %s, got %s" %
                    (str(types), ntype), node)


def advance(parser):
    if parser.isend():
        return None

    node = parser.next_token()
    # print "ADVANCE", node
    return node


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    return advance(parser)


def advance_expected_one_of(parser, ttypes):
    check_token_types(parser, ttypes)

    if parser.isend():
        return None

    return parser.next_token()


def endofexpression(parser):
    res = parser.on_endofexpression()
    if res is False:
        parse_error(parser,
                    "Expected end of expression mark got '%s'" %
                    parser.token.value,
                    parser.node)

    return res


def base_expression(parser, _rbp, terminators=None):
    previous = parser.node
    if node_has_layout(parser, previous):
        node_layout(parser, previous)

    advance(parser)

    left = node_nud(parser, previous)
    while True:
        # if parser.is_newline_occurred:
        #     break

        if terminators is not None:
            if parser.token_type in terminators:
                return left

        _lbp = node_lbp(parser, parser.node)

        # juxtaposition support
        if _lbp < 0:
            if parser.break_on_juxtaposition is True:
                return left

            op = parser_operator(parser, parser.lex.TT_JUXTAPOSITION)
            _lbp = op.lbp

            if _rbp >= _lbp:
                break
            previous = parser.node
            # advance(parser)
            if not op.led:
                parse_error(parser, "Unknown token led", previous)

            left = op.led(parser, op, previous, left)
        else:
            if _rbp >= _lbp:
                break
            previous = parser.node
            advance(parser)

            left = node_led(parser, previous, left)

    assert left is not None
    return left


def expect_expression_of(parser, _rbp, expected_type, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_type(parser, exp, expected_type)
    return exp


def expect_expression_of_types(parser, _rbp, expected_types, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_types(parser, exp, expected_types)
    return exp


def skip_token(parser, token_type):
    if parser.token_type == token_type:
        advance(parser)


# TODO mandatory terminators
def expression(parser, _rbp, terminators=None):
    if not terminators:
        terminators = [parser.lex.TT_END_EXPR]
    expr = base_expression(parser, _rbp, terminators)
    expr = parser.postprocess(expr)
    return expr


# INFIXR
def rexpression(parser, op, terminators):
    return expression(parser, op.lbp - 1, terminators)


def literal_expression(parser):
    # Override most operators in literals
    # because of prefix operators
    return expression(parser, 70)


def statement(parser):
    node = parser.node
    if node_has_std(parser, node):
        advance(parser)
        value = node_std(parser, node)
        return value

    value = expression(parser, 0)
    return value


def statement_no_end_expr(parser):
    node = parser.node
    if node_has_std(parser, node):
        advance(parser)
        value = node_std(parser, node)
        return value

    value = expression(parser, 0)
    return value


def statements(parser, endlist):
    stmts = []
    while True:
        if token_is_one_of(parser, endlist):
            break
        s = statement(parser)
        end_exp = parser.on_endofexpression()
        if s is None:
            continue
        stmts.append(s)
        if end_exp is False:
            break

    length = len(stmts)
    if length == 0:
        return parse_error(parser,
                           "Expected one or more expressions", parser.node)

    return nodes.list_node(stmts)


# def statements(parser, endlist):
#     return _statements(parser, statement, endlist)
#
#
# def module_statements(parser, endlist):
#     return _statements(parser, statement_no_end_expr, endlist)

def parser_set_layout(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.layout = fn
    return h


def parser_set_nud(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.nud = fn
    return h


def parser_set_std(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.std = fn
    return h


def parser_set_led(parser, ttype, lbp, fn):
    h = get_or_create_operator(parser, ttype)
    h.lbp = lbp
    h.led = fn
    return h


def operator_infix(h, lbp, led, infix_fn):
    h.lbp = lbp
    h.led = led
    h.infix_function = infix_fn
    return h


def operator_prefix(h, nud, prefix_fn):
    h.nud = nud
    h.prefix_function = prefix_fn
    return h


def infix(parser, ttype, lbp, led):
    parser_set_led(parser, ttype, lbp, led)


def prefix(parser, ttype, nud, layout=None):
    parser_set_nud(parser, ttype, nud)
    parser_set_layout(parser, ttype, layout)


def stmt(parser, ttype, std):
    parser_set_std(parser, ttype, std)


def prefix_nud(parser, op, node):
    exp = literal_expression(parser)
    return nodes.node_1(parser.lex.get_nt_for_node(node),
                        node.token, exp)


def itself(parser, op, node):
    return nodes.node_0(parser.lex.get_nt_for_node(node),
                        node.token)


def literal(parser, ttype):
    parser_set_nud(parser, ttype, itself)


def symbol(parser, ttype, nud=None):
    h = get_or_create_operator(parser, ttype)
    h.lbp = 0
    parser_set_nud(parser, ttype, nud)
    return h


def skip(parser, ttype):
    while parser.token_type == ttype:
        advance(parser)


def empty(parser, op, node):
    return expression(parser, 0)


def led_infix(parser, op, node, left):
    exp = expression(parser, op.lbp)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token,
                        left, exp)


def led_infixr(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token,
                        left, exp)


def led_infixr_assign(parser, op, node, left):
    exp = expression(parser, 9)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token, left, exp)


def infixr(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr)


def assignment(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr_assign)


def _parse(parser, termination_tokens):
    parser.enter_scope()
    stmts = statements(parser, termination_tokens)
    scope = parser.exit_scope()
    return stmts, scope


def parse_token_stream(parser, ts):
    parser.open(ParseState(ts))
    parser.next_token()
    stmts, scope = _parse(parser, [parser.lex.TT_ENDSTREAM])
    assert len(parser.state.scopes) == 0
    check_token_type(parser, parser.lex.TT_ENDSTREAM)
    parser.close()
    return stmts, scope
