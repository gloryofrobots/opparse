from opparse.parse import nodes, tokens, lexer
from opparse.misc.strutil import get_line, get_line_for_position
from opparse import plist
import operator
from opparse.parse.indenter import InvalidIndentationError


class ParseError(RuntimeError):
    pass


def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    raise ParseError([
        position,
        u"Unknown Token",
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
    if nodes.node_token_type(node) == parser.lex.TT_ENDSTREAM:
        line = u"Unclosed top level statement"
    else:
        line = get_line(parser.ts.src, nodes.node_line(node))

    raise ParseError([
        nodes.node_position(node),
        nodes.node_line(node),
        nodes.node_column(node),
        nodes.node_to_string(node),
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


class ParserScope(object):

    def __init__(self):
        self.operators = {}
        self.macro = {}


class ParseState:

    def __init__(self, ts, lexicon):
        self.ts = ts
        self.lexicon = lexicon
        self.scopes = plist.empty()


def parser_enter_scope(parser):
    parser.state.scopes = plist.cons(ParserScope(), parser.state.scopes)


def parser_exit_scope(parser):
    head = plist.head(parser.state.scopes)
    parser.state.scopes = plist.tail(parser.state.scopes)
    return head


def parser_current_scope(parser):
    return plist.head(parser.state.scopes)


def parser_current_scope_add_operator(parser, op_name, op):
    cur_scope = parser_current_scope(parser)
    operator.setitem(cur_scope.operators, op_name, op)


def parser_current_scope_find_operator_or_create_new(parser, op_name):
    cur_scope = parser_current_scope(parser)
    op = cur_scope.operators.get(op_name, None)
    if op is None:
        return newoperator()
    return op


def parser_find_operator(parser, op_name):
    undef = None
    scopes = parser.state.scopes
    for scope in scopes:
        op = scope.operators.get(op_name, undef)
        if op is not None:
            return op

    return None


class W_Operator(object):

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
        if not isinstance(other, W_Operator):
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
        return '<operator %s %s>' % (self.prefix_s(), self.infix_s())


def newoperator():
    return W_Operator()


def parser_has_operator(parser, ttype):
    return ttype in parser.handlers


def parser_operator(parser, ttype):
    assert ttype <= parser.lex.TT_UNKNOWN
    try:
        return parser.handlers[ttype]
    except:
        if ttype == parser.lex.TT_UNKNOWN:
            return parse_error(parser, u"Invalid token", parser.node)

        if parser.allow_unknown is True:
            return parser_operator(parser, parser.lex.TT_UNKNOWN)
        return parse_error(parser,
                           u"Invalid token %s" % tokens.token_type_to_s(ttype),
                           parser.node)


def get_or_create_operator(parser, ttype):
    if not parser_has_operator(parser, ttype):
        return parser_set_operator(parser, ttype, newoperator())
    return parser_operator(parser, ttype)


def parser_set_operator(parser, ttype, h):
    parser.handlers[ttype] = h
    return parser_operator(parser, ttype)


def node_operator(parser, node):
    ttype = nodes.node_token_type(node)
    if not parser.allow_overloading:
        return parser_operator(parser, ttype)

    if ttype != parser.lex.TT_OPERATOR:
        return parser_operator(parser, ttype)

    # in case of operator
    op = parser_find_operator(parser, nodes.node_value(node))
    if op is None:
        return parse_error(parser, u"Invalid operator", node)
    return op


def node_nud(parser, node):
    handler = node_operator(parser, node)
    if not handler.nud:
        parse_error(parser, u"Unknown token nud", node)
    return handler.nud(parser, handler, node)


def node_std(parser, node):
    handler = node_operator(parser, node)
    if not handler.std:
        parse_error(parser, u"Unknown token std", node)

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
    #   parse_error(parser, u"Left binding power error", node)

    return lbp


def node_led(parser, node, left):
    handler = node_operator(parser, node)
    if not handler.led:
        parse_error(parser, u"Unknown token led", node)

    return handler.led(parser, handler, node, left)


def node_layout(parser, node):
    handler = node_operator(parser, node)
    if not handler.layout:
        parse_error(parser, u"Unknown token layout", node)

    return handler.layout(parser, handler, node)


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


def token_is_one_of(parser, types):
    return parser.token_type in types


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser,
                    u"Wrong token type, expected %s, got %s" %
                    (tokens.token_type_to_s(type),
                     tokens.token_type_to_s(parser.token_type)),
                    parser.node)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, u"Wrong token type, expected one of %s, got %s" %
                    (unicode([tokens.token_type_to_s(type) for type in types]),
                     tokens.token_type_to_s(parser.token_type)), parser.node)


def check_list_node_types(parser, node, expected_types):
    for child in node:
        check_node_types(parser, child, expected_types)


def check_node_type(parser, node, expected_type):
    ntype = nodes.node_type(node)
    if ntype != expected_type:
        parse_error(parser, u"Wrong node type, expected  %s, got %s" %
                    expected_type, ntype, node)


def check_node_types(parser, node, types):
    ntype = nodes.node_type(node)
    if ntype not in types:
        parse_error(parser, u"Wrong node type, expected one of %s, got %s" %
                    str(types), ntype, node)


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
                    u"Expected end of expression mark got '%s'" %
                    tokens.token_value(parser.token),
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
                parse_error(parser, u"Unknown token led", previous)

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


def juxtaposition_as_list(parser, terminators):
    node = parser.node
    exp = expression(parser, 0, terminators)
    if not nodes.is_list_node(exp):
        return nodes.create_list_node(node, [exp])

    return nodes.create_list_node_from_list(node, exp)


def juxtaposition_as_tuple(parser, terminators):
    node = parser.node
    exp = expression(parser, 0, terminators)
    if not nodes.is_list_node(exp):
        return nodes.create_tuple_node(node, [exp])

    return nodes.create_tuple_node_from_list(node, exp)


def flatten_juxtaposition(parser, node):
    ntype = nodes.node_type(node)
    if ntype == parser.lex.NT_JUXTAPOSITION:
        first = nodes.node_first(node)
        second = nodes.node_second(node)
        head = flatten_juxtaposition(parser, first)
        tail = flatten_juxtaposition(parser, second)
        return plist.concat(head, tail)
    else:
        return nodes.list_node([node])


def postprocess(parser, node):
    if nodes.is_empty_node(node):
        return node
    elif nodes.is_list_node(node):
        children = []
        for c in node:
            children.append(postprocess(parser, c))
        return nodes.list_node(children)

    ntype = nodes.node_type(node)
    if ntype == parser.lex.NT_JUXTAPOSITION:
        flatten = flatten_juxtaposition(parser, node)
        # probably overkill
        if len(flatten) < 2:
            parse_error(parser, u"Invalid use of juxtaposition operator", node)

        if parser.juxtaposition_as_list:
            return postprocess(parser, flatten)
        else:
            caller = plist.head(flatten)
            args = plist.tail(flatten)
            return postprocess(parser,
                               nodes.node_2(parser.lex.NT_CALL,
                                            nodes.node_token(caller),
                                            caller, args))
    else:
        children = []
        node_children = nodes.node_children(node)
        if node_children is None:
            return node

        for c in node_children:
            new_child = postprocess(parser, c)
            children.append(new_child)
        return nodes.newnode(nodes.node_type(node),
                             nodes.node_token(node), children)


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
                           u"Expected one or more expressions", parser.node)

    return nodes.list_node(stmts)


# def statements(parser, endlist):
#     return _statements(parser, statement, endlist)
#
#
# def module_statements(parser, endlist):
#     return _statements(parser, statement_no_end_expr, endlist)


def infix(parser, ttype, lbp, led):
    parser_set_led(parser, ttype, lbp, led)


def prefix(parser, ttype, nud, layout=None):
    parser_set_nud(parser, ttype, nud)
    parser_set_layout(parser, ttype, layout)


def stmt(parser, ttype, std):
    parser_set_std(parser, ttype, std)


def literal(parser, ttype):
    from opparse.parse.callbacks import itself
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
                        nodes.node_token(node),
                        left, exp)


def led_infixr(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        nodes.node_token(node),
                        left, exp)


def led_infixr_assign(parser, op, node, left):
    exp = expression(parser, 9)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        nodes.node_token(node), left, exp)


def infixr(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr)


def assignment(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr_assign)


class Parser:

    def __init__(self, allow_overloading=False,
                 break_on_juxtaposition=False, allow_unknown=True,
                 juxtaposition_as_list=True):
        self.handlers = {}
        self.state = None
        self.allow_overloading = allow_overloading
        self.break_on_juxtaposition = break_on_juxtaposition
        self.allow_unknown = allow_unknown
        self.juxtaposition_as_list = juxtaposition_as_list

        self.subparsers = {}

    def add_subparser(self, parser_name, parser):
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
    def lex(self):
        return self.state.lexicon

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
        except lexer.UnknownTokenError as e:
            parser_error_unknown(self, e.position)

    def isend(self):
        return self.token_type == self.lex.TT_ENDSTREAM


def parse_script(parser, termination_tokens):
    parser_enter_scope(parser)
    stmts = statements(parser, termination_tokens)
    scope = parser_exit_scope(parser)
    return stmts, scope


def parse(parser, ts, lexicon):
    parser.open(ParseState(ts, lexicon))
    parser.next_token()
    stmts, scope = parse_script(parser, [parser.lex.TT_ENDSTREAM])
    assert plist.is_empty(parser.state.scopes)
    check_token_type(parser, parser.lex.TT_ENDSTREAM)
    parser.close()
    return stmts, scope
