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
        parser.advance()


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


class Parser:

    def __init__(self, name, lexicon, operators, settings):

        self.name = name
        self.lex = lexicon
        self.operators = operators
        self.allow_overloading = settings.get("allow_overloading", False)
        self.break_on_juxtaposition = \
            settings.get("break_on_juxtaposition", False)
        self.allow_unknown = settings.get("allow_unknown", True)
        self.juxtaposition_as_list = \
            settings.get("juxtaposition_as_list", False)

        self.subparsers = {}
        self.state = None

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

    ## OPERATORS

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
                return parse_error(self, "Invalid token", self.node)

            if self.allow_unknown is True:
                return self.operator(self.lex.TT_UNKNOWN)
            return parse_error(self,
                               "Invalid token %s" % ttype,
                               self.node)

    
    def node_operator(self, node):
        ttype = node.token_type
        if not self.allow_overloading:
            return self.operator(ttype)

        if ttype != self.lex.TT_OPERATOR:
            return self.operator(ttype)

        # in case of custom operator
        op = self.find_custom_operator(node.token_value)
        if op is None:
            return parse_error(self, "Invalid operator", node)
        return op


    def node_nud(self, node):
        handler = self.node_operator(node)
        if not handler.nud:
            parse_error(self, "Unknown token nud", node)
        return handler.nud(self, handler, node)


    def node_std(self, node):
        handler = self.node_operator(node)
        if not handler.std:
            parse_error(self, "Unknown token std", node)

        return handler.std(self, handler, node)


    def node_has_nud(self, node):
        handler = self.node_operator(node)
        return handler.nud is not None


    def node_has_layout(self, node):
        handler = self.node_operator(node)
        return handler.layout is not None


    def node_has_led(self, node):
        handler = self.node_operator(node)
        return handler.led is not None


    def node_has_std(self, node):
        handler = self.node_operator(node)
        return handler.std is not None


    def node_lbp(self, node):
        handler = self.node_operator(node)
        lbp = handler.lbp
        # if lbp < 0:
        #   parse_error(self, "Left binding power error", node)

        return lbp


    def node_led(self, node, left):
        handler = self.node_operator(node)
        if not handler.led:
            parse_error(self, "Unknown token led", node)

        return handler.led(self, handler, node, left)


    def node_layout(self, node):
        handler = self.node_operator(node)
        if not handler.layout:
            parse_error(self, "Unknown token layout", node)

        return handler.layout(self, handler, node)


    # ASSERTIONS
    
    def token_is_one_of(self, types):
        return self.token_type in types


    def assert_token_type(self, type):
        if self.token_type != type:
            parse_error(self,
                        "Wrong token type, expected %s, got %s" %
                        (type, self.token_type),
                        self.node)


    def assert_token_types(self, types):
        if self.token_type not in types:
            parse_error(self, "Wrong token type, expected one of %s, got %s" %
                        (unicode([type for type in types]),
                        self.token_type), parser.node)


    def assert_types_in_nodes_list(self, node, expected_types):
        for child in node:
            self.assert_node_types(child, expected_types)


    def assert_node_type(self, node, expected_type):
        ntype = node.node_type
        if ntype != expected_type:
            parse_error(self, "Wrong node type, expected  %s, got %s" %
                        (expected_type, ntype), node)


    def assert_node_types(self, node, types):
        ntype = node.node_type
        if ntype not in types:
            parse_error(self, "Wrong node type, expected one of %s, got %s" %
                        (str(types), ntype), node)

    def advance(self):
        if self.isend():
            return None

        node = self.next_token()
        # print "ADVANCE", node
        return node


    def advance_expected(self, ttype):
        self.assert_token_type(ttype)

        return self.advance()


    def advance_expected_one_of(self, ttypes):
        self.assert_token_types(ttypes)

        if self.isend():
            return None

        return self.next_token()

    # PARSING
    def endofexpression(self):
        if self.isend():
            return None
        if self.token_type == self.lex.TT_END_EXPR:
            return self.advance()
        return False



    def base_expression(self, _rbp, terminators):
        previous = self.node
        if self.node_has_layout(previous):
            self.node_layout(previous)

        self.advance()

        left = self.node_nud(previous)
        while True:
            # if self.is_newline_occurred:
            #     break

            if terminators is not None:
                if self.token_type in terminators:
                    return left

            _lbp = self.node_lbp(self.node)

            # juxtaposition support
            if _lbp < 0:
                if self.break_on_juxtaposition is True:
                    return left

                op = self.operator(self.lex.TT_JUXTAPOSITION)
                _lbp = op.lbp

                if _rbp >= _lbp:
                    break
                previous = self.node
                # self.advance()
                if not op.led:
                    parse_error(self, "Unknown token led", previous)

                left = op.led(self, op, previous, left)
            else:
                if _rbp >= _lbp:
                    break
                previous = self.node
                self.advance()

                left = self.node_led(previous, left)

        assert left is not None
        return left


def expect_expression_of(parser, _rbp, expected_type, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    parser.assert_node_type(exp, expected_type)
    return exp


def expect_expression_of_types(parser, _rbp, expected_types, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    parser.assert_node_types(exp, expected_types)
    return exp




# TODO mandatory terminators
def expression(parser, _rbp, terminators=None):
    if not terminators:
        terminators = [parser.lex.TT_END_EXPR]
    expr = parser.base_expression(_rbp, terminators)
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
    if parser.node_has_std(node):
        parser.advance()
        value = parser.node_std(node)
        return value

    value = expression(parser, 0)
    return value


def statement_no_end_expr(parser):
    node = parser.node
    if parser.node_has_std(node):
        parser.advance()
        value = parser.node_std(node)
        return value

    value = expression(parser, 0)
    return value


def statements(parser, endlist):
    stmts = []
    while True:
        if parser.token_is_one_of(endlist):
            break
        s = statement(parser)
        end_exp = parser.endofexpression()
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


def skip_token(parser, token_type):
    if parser.token_type == token_type:
        parser.advance()

def skip(parser, ttype):
    while parser.token_type == ttype:
        parser.advance()

##########################################################################
## COMMON CALLBACKS #######################################################
##########################################################################

def prefix_itself(parser, op, node):
    return nodes.node_0(parser.lex.get_nt_for_node(node),
                        node.token)

def prefix_empty(parser, op, node):
    return expression(parser, 0)


def prefix_nud(parser, op, node):
    exp = literal_expression(parser)
    return nodes.node_1(parser.lex.get_nt_for_node(node),
                        node.token, exp)


def infix_led(parser, op, node, left):
    exp = expression(parser, op.lbp)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token,
                        left, exp)


def infixr_led(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token,
                        left, exp)


def infixr_led_assign(parser, op, node, left):
    exp = expression(parser, 9)
    return nodes.node_2(parser.lex.get_nt_for_node(node),
                        node.token, left, exp)

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

    def layout(self, ttype, fn):
        self.operators.set_layout(ttype, fn)
        return self

    def infix(self, ttype, lbp, led):
        self.operators.set_led(ttype, lbp, led)
        return self

    def prefix(self, ttype, nud, layout=None):
        self.operators.set_nud(ttype, nud)
        self.operators.set_layout(ttype, layout)
        return self

    def stmt(self, ttype, std):
        self.operators.set_std(ttype, std)
        return self

    def literal(self, ttype):
        self.operators.set_nud(ttype, prefix_itself)
        return self

    def symbol(self, ttype, nud=None):
        self.operators.set_lbp(ttype, 0)
        self.operators.set_nud(ttype, nud)
        return self

    def infixr(self, ttype, lbp):
        return self.infix(ttype, lbp, infixr_led)

    def assignment(self, ttype, lbp):
        return self.infix(ttype, lbp, infixr_led_assign)
        

    def build(self, name):
        return self.parser_class(name, self.lexicon,
                                 self.operators, self.settings)



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
    parser.assert_token_type(parser.lex.TT_ENDSTREAM)
    parser.close()
    return stmts, scope
