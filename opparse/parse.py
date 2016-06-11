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


def parse_error(parser, message, token):
    print parser.ts.advanced_values()
    print parser.ts.layouts
    if token.type == parser.lex.TT_ENDSTREAM:
        line = "Unclosed top level statement"
    else:
        line = get_line(parser.ts.src, token.line)

    raise ParseError([
        token.position,
        token.line,
        token.column,
        str(token),
        message,
        line
    ])

##########################################################################
# COMMON CALLBACKS #######################################################
##########################################################################


def prefix_itself(parser, op, token):
    return nodes.node_0(op.prefix_node_type, token)


def prefix_empty(parser, op, token):
    return nodes.empty_node()


def prefix_nud(parser, op, token):
    exp = parser.literal_expression()
    return nodes.node_1(op.prefix_node_type, token, exp)


def infix_led(parser, op, token, left):
    exp = parser.expression(op.lbp)
    return nodes.node_2(op.infix_node_type, token, left, exp)


def infixr_led(parser, op, token, left):
    exp = parser.rexpression(op)
    return nodes.node_2(op.infix_node_type, token, left, exp)


def infixr_led_assign(parser, op, token, left):
    exp = parser.expression(op.lbp - 1)
    return nodes.node_2(op.infix_node_type, token, left, exp)
# LAYOUT


def flatten_infix(node, ttype):
    if node.node_type == ttype:
        first = node.first()
        second = node.second()
        head = flatten_infix(first, ttype)
        tail = flatten_infix(second, ttype)
        return head.concat(tail)
    else:
        return nodes.list_node([node])


def parse_struct(parser, func, terminator, separator, initializer=None):
    items = []
    if parser.token_type != terminator:
        if initializer:
            initializer(parser)
        while parser.token_type != terminator:
            items.append(func(parser))
            if parser.token_type != separator:
                break

            parser.advance_expected(separator)
    parser.advance_expected(terminator)
    return nodes.list_node(items)


class Operator(object):

    def __init__(self):
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1
        # self.is_breaker = False
        self.layout = None

        self.prefix_node_type = None
        self.infix_node_type = None
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
            if self.prefix_function != other.prefix_function:
                return False
        elif self.prefix_function or other.prefix_function:
            return False

        if self.infix_function and other.infix_function:
            if self.infix_function != other.infix_function:
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


class Operators:

    def __init__(self):
        self.__operators = {}

    def set_nud(self, ttype, fn):
        h = self.get_or_create(ttype)
        h.nud = fn
        return h

    def set_layout(self, ttype, layout):
        h = self.get_or_create(ttype)
        h.layout = layout
        return h

    def set_std(self, ttype, fn):
        h = self.get_or_create(ttype)
        h.std = fn
        return h

    def set_led(self, ttype, lbp, fn):
        h = self.get_or_create(ttype)
        h.lbp = lbp
        h.led = fn
        return h

    def set_lbp(self, ttype, lbp):
        h = self.get_or_create(ttype)
        h.lbp = lbp

    def set_infix_function(self, h, lbp, led, infix_fn):
        h.lbp = lbp
        h.led = led
        h.infix_function = infix_fn
        return h

    def set_prefix_function(self, h, nud, prefix_fn):
        h.nud = nud
        h.prefix_function = prefix_fn
        return h

    def set_prefix_node_type(self, ttype, node_type):
        h = self.get_or_create(ttype)
        h.prefix_node_type = node_type
        return h

    def set_infix_node_type(self, ttype, node_type):
        h = self.get_or_create(ttype)
        h.infix_node_type = node_type
        return h

    def has(self, ttype):
        return ttype in self.__operators

    def get(self, ttype):
        return self.__operators[ttype]

    def get_or_create(self, ttype):
        if not self.has(ttype):
            self.__operators[ttype] = Operator()
        return self.get(ttype)


class ParseState:

    def __init__(self, ts):
        self.ts = ts
        self.scopes = []


class Parser(object):

    def __init__(self, name, lexicon, operators, settings):

        self.name = name
        self.lex = lexicon
        self.operators = operators

        self.subparsers = {}
        self.state = None

        self.allow_overloading = settings.get("allow_overloading", False)
        self.allow_unknown = settings.get("allow_unknown", True)

    def add_builder(self, name, builder):
        parser = builder.build(name)
        return self.add_subparser(parser)

    def add_subparser(self, parser):
        setattr(self, parser.name, parser)
        self.subparsers[parser.name] = parser
        return self

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

    # OPERATORS

    def find_custom_operator(self, op_name):
        scopes = self.state.scopes
        for scope in scopes:
            op = scope.custom_operators.get(op_name, None)
            if op is not None:
                return op

        return None

    def operator(self, ttype):
        try:
            return self.operators.get(ttype)
        except:
            if ttype == self.lex.TT_UNKNOWN:
                return parse_error(self, "Invalid token", self.token)

            if self.allow_unknown is True:
                return self.operator(self.lex.TT_UNKNOWN)
            return parse_error(self,
                               "Invalid token %s" % ttype,
                               self.token)

    def token_operator(self, token):
        assert isinstance(token, lexer.Token)
        ttype = token.type
        if not self.allow_overloading:
            return self.operator(ttype)

        if ttype != self.lex.TT_OPERATOR:
            return self.operator(ttype)

        # in case of custom operator
        op = self.find_custom_operator(token.value)
        if op is None:
            return parse_error(self, "Invalid operator", token)
        return op

    def token_nud(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        if not handler.nud:
            parse_error(self, "Unknown token nud", token)
        return handler.nud(self, handler, token)

    def token_std(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        if not handler.std:
            parse_error(self, "Unknown token std", token)

        return handler.std(self, handler, token)

    def token_has_nud(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        return handler.nud is not None

    def token_has_layout(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        return handler.layout is not None

    def token_has_led(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        return handler.led is not None

    def token_has_std(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        return handler.std is not None

    def token_lbp(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        lbp = handler.lbp
        if lbp < 0:
            parse_error(self, "Left binding power error", token)

        return lbp

    def token_led(self, token, left):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        if not handler.led:
            parse_error(self, "Unknown token led", token)

        return handler.led(self, handler, token, left)

    def token_layout(self, token):
        assert isinstance(token, lexer.Token)
        handler = self.token_operator(token)
        if not handler.layout:
            parse_error(self, "Unknown token layout", token)

        return handler.layout(self, handler, token)

    # ASSERTIONS

    def token_is_one_of(self, types):
        return self.token_type in types

    def assert_token_type(self, type):
        if self.token_type != type:
            parse_error(self,
                        "Wrong token type, expected %s, got %s" %
                        (type, self.token_type),
                        self.token)

    def assert_token_types(self, types):
        if self.token_type not in types:
            parse_error(self, "Wrong token type, expected one of %s, got %s" %
                        (unicode([type for type in types]),
                         self.token_type), self.token)

    def assert_types_in_nodes_list(self, node, expected_types):
        for child in node:
            self.assert_node_types(child, expected_types)

    def assert_node_type(self, node, expected_type):
        ntype = node.node_type
        if ntype != expected_type:
            parse_error(self, "Wrong node type, expected  %s, got %s" %
                        (expected_type, ntype), node.token)

    # MOVEMENTS

    def assert_node_types(self, node, types):
        ntype = node.node_type
        if ntype not in types:
            parse_error(self, "Wrong node type, expected one of %s, got %s" %
                        (str(types), ntype), node.token)

    def advance(self):
        if self.isend():
            return None

        token = self.next_token()
        return token

    def advance_expected(self, ttype):
        self.assert_token_type(ttype)

        return self.advance()

    def advance_expected_one_of(self, ttypes):
        self.assert_token_types(ttypes)

        if self.isend():
            return None

        return self.next_token()

    def skip_while(parser, ttype):
        while parser.token_type == ttype:
            parser.advance()

    def skip_once(parser, token_type):
        if parser.token_type == token_type:
            parser.advance()

    # PARSING
    def endofexpression(self):
        if self.isend():
            return False
        if self.token_type == self.lex.TT_END_EXPR:
            self.advance()
            return True
        return False

    def base_expression(self, _rbp, terminators):
        previous = self.token
        if self.token_has_layout(previous):
            self.token_layout(previous)

        self.advance()

        left = self.token_nud(previous)
        while True:
            if terminators is not None:
                if self.token_type in terminators:
                    return left

            _lbp = self.token_lbp(self.token)

            if _rbp >= _lbp:
                break
            previous = self.token
            self.advance()

            left = self.token_led(previous, left)

        assert left is not None
        return left

    def expression(self, rbp):
        return self.terminated_expression(rbp, None)

    def terminated_expression(self, rbp, terminators):
        # if not terminators:
        #     terminators = [self.lex.TT_END_EXPR]
        expr = self.base_expression(rbp, terminators)
        expr = self.postprocess(expr)
        return expr

    def postprocess(self, expr):
        return expr

    def assert_expression(self, rbp, expected_type):
        return self.assert_terminated_expression(rbp, expected_type, None)

    def assert_terminated_expression(
            self, rbp, expected_type, terminators):
        exp = self.terminated_expression(rbp, terminators)
        self.assert_node_type(exp, expected_type)
        return exp

    def assert_any_of_terminated_expressions(
            self, rbp, expected_types, terminators):

        exp = self.terminated_expression(rbp, terminators)
        self.assert_node_types(exp, expected_types)
        return exp

    def assert_any_of_expressions(self, rbp, expected_types):
        return self.assert_any_of_terminated_expressions(
            rbp, expected_types, None)

    def rexpression(self, op):
        return self.expression(op.lbp - 1)

    def terminated_rexpression(self, op, terminators):
        return self.terminated_expression(op.lbp - 1, terminators)

    def literal_expression(self):
        # Override most operators in literals
        # because of prefix operators
        return self.expression(70)

    def statement(self):
        token = self.token
        if self.token_has_std(token):
            self.advance()
            value = self.token_std(token)
            return value

        value = self.expression(0)
        return value

    def statements(self, endlist):
        stmts = []
        while True:
            if self.token_is_one_of(endlist):
                break
            s = self.statement()
            # order matter here
            continue_loop = self.endofexpression()
            if nodes.is_empty_node(s):
                continue

            stmts.append(s)
            if continue_loop is False:
                break

        length = len(stmts)
        if length == 0:
            return parse_error(self,
                               "Expected one or more expressions",
                               self.token)

        return nodes.list_node(stmts)


class JuxtapositionParser(Parser):

    def __init__(self, name, lexicon, operators, settings):
        super(JuxtapositionParser, self).__init__(
            name, lexicon, operators, settings)

        self.allow_overloading = settings.get("allow_overloading", False)
        self.allow_unknown = settings.get("allow_unknown", True)

        self.juxtaposition_as_list = \
            settings.get("juxtaposition_as_list", False)
        self.break_on_juxtaposition = \
            settings.get("break_on_juxtaposition", False)

    def token_lbp(self, token):
        operator = self.token_operator(token)
        lbp = operator.lbp
        # if lbp < 0:
        #   parse_error(self, "Left binding power error", token)

        return lbp

    def flatten_juxtaposition(self, node):
        ntype = node.node_type
        if ntype == self.lex.NT_JUXTAPOSITION:
            first = node.first()
            second = node.second()
            head = self.flatten_juxtaposition(first)
            tail = self.flatten_juxtaposition(second)
            return head.concat(tail)
        else:
            return nodes.list_node([node])

    def base_expression(self, _rbp, terminators):
        previous = self.token
        if self.token_has_layout(previous):
            self.token_layout(previous)

        self.advance()

        left = self.token_nud(previous)
        while True:
            if terminators is not None:
                if self.token_type in terminators:
                    return left

            _lbp = self.token_lbp(self.token)

            # juxtaposition support
            if _lbp < 0:
                if self.break_on_juxtaposition is True:
                    return left

                op = self.operator(self.lex.TT_JUXTAPOSITION)
                _lbp = op.lbp

                if _rbp >= _lbp:
                    break
                previous = self.token
                if not op.led:
                    parse_error(self, "Unknown token led", previous)

                left = op.led(self, op, previous, left)
            else:
                if _rbp >= _lbp:
                    break
                previous = self.token
                self.advance()

                left = self.token_led(previous, left)

        assert left is not None
        return left

    def postprocess(self, node):
        if nodes.is_empty_node(node):
            return node

        elif nodes.is_list_node(node):
            children = []
            for c in node:
                children.append(self.postprocess(c))
            return nodes.list_node(children)

        ntype = node.node_type
        if ntype == self.lex.NT_JUXTAPOSITION:
            flatten = self.flatten_juxtaposition(node)
            assert len(flatten) >= 2

            if self.juxtaposition_as_list:
                return self.postprocess(flatten)
            else:
                caller = flatten.head()
                args = flatten.tail()
                return self.postprocess(
                    nodes.node_2(self.lex.NT_CALL,
                                 caller.token,
                                 caller, args))
        else:
            children = []
            node_children = node.children
            if node_children is None:
                return node

            for c in node_children:
                new_child = self.postprocess(c)
                children.append(new_child)
            return nodes.Node(node.node_type, node.token, children)


##############################################################


class Builder:
    DEFAULT_CLASS = Parser

    def __init__(self, lexicon, settings, parser_class=None):
        self.lexicon = lexicon
        self.settings = settings
        self.operators = Operators()
        if parser_class is None:
            self.parser_class = self.DEFAULT_CLASS
        else:
            assert issubclass(parser_class, Parser), parser_class
            self.parser_class = parser_class

    def infix(self, ttype, lbp, led, node_type=None):
        self.operators.set_led(ttype, lbp, led)
        self.operators.set_infix_node_type(ttype, node_type)
        return self

    def infix_default(self, ttype, lbp, node_type):
        self.infix(ttype, lbp, infix_led, node_type)
        return self

    def infixr(self, ttype, lbp, node_type):
        self.infix(ttype, lbp, infixr_led, node_type)
        return self

    def assignment(self, ttype, lbp, node_type):
        return self.infix(ttype, lbp, infixr_led_assign, node_type)

    def prefix_layout(self, ttype, nud, layout, node_type=None):
        self.prefix(ttype, nud, node_type, layout)
        return self

    def prefix(self, ttype, nud, node_type=None, layout=None):
        self.operators.set_nud(ttype, nud)
        self.operators.set_prefix_node_type(ttype, node_type)
        self.operators.set_layout(ttype, layout)
        return self

    def prefix_default(self, ttype, node_type):
        self.prefix(ttype, prefix_nud, node_type)
        return self

    def literal(self, ttype, node_type):
        self.prefix(ttype, prefix_itself, node_type=node_type, layout=None)
        return self

    def symbol(self, ttype, nud=None):
        self.operators.set_lbp(ttype, 0)
        self.operators.set_nud(ttype, nud)
        return self

    def stmt(self, ttype, std):
        self.operators.set_std(ttype, std)
        return self

    def build(self, name):
        return self.parser_class(name, self.lexicon,
                                 self.operators, self.settings)


def _parse(parser, termination_tokens):
    parser.enter_scope()
    stmts = parser.statements(termination_tokens)
    scope = parser.exit_scope()
    return stmts, scope


def parse_token_stream(parser, ts):
    parser.open(ParseState(ts))
    parser.next_token()
    stmts, scope = _parse(parser, [parser.lex.TT_ENDSTREAM])
    assert len(parser.state.scopes) == 0
    parser.assert_token_type(parser.lex.TT_ENDSTREAM)
    parser.close()
    return stmts, scope
