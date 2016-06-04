from opparse.parse import nodes
from opparse.parse import tokens
from opparse import plist
from opparse.misc.fifo import Fifo

LOG_INDENTER = False


class InvalidIndentationError(Exception):

    def __init__(self, msg, position, line, column):
        self.position = position
        self.line = line
        self.column = column
        self.msg = msg

    def __str__(self):
        return self.msg


MODULE = -1
NODE = 0
CODE = 1
OFFSIDE = 2
FREE = 3


def log(*args):
    if not LOG_INDENTER:
        return
    print ", ".join([str(arg) for arg in args])


class Layout(object):

    def __init__(self, parent_level, level, type, level_tokens, terminators):
        self.parent_level = parent_level
        self.level = level
        self.type = type
        self.level_tokens = level_tokens if level_tokens else []
        self.terminators = terminators if terminators else []

    def has_level(self, token_type):
        return token_type in self.level_tokens

    def has_terminator(self, token_type):
        return token_type in self.terminators

    @property
    def push_end_of_expression_on_new_line(self):
        return self.type == CODE or self.type == MODULE

    @property
    def push_end_on_dedent(self):
        return self.type == NODE

    @property
    def push_end_of_expression_on_dedent(self):
        return self.type == NODE

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        bt = self.type
        bt_s = None
        if bt == CODE:
            bt_s = "CHILD"
        elif bt == FREE:
            bt_s = "FREE"
        elif bt == MODULE:
            bt_s = "MODULE"
        elif bt == NODE:
            bt_s = "NODE"
        elif bt == OFFSIDE:
            bt_s = "OFFSIDE"
        return "<Block pl=%d, l=%d, t=%s>" % \
            (self.parent_level, self.level, bt_s)

    def is_code(self):
        return self.type == CODE

    def is_node(self):
        return self.type == NODE

    def is_free(self):
        return self.type == FREE

    def is_module(self):
        return self.type == MODULE


def indentation_error(msg, token):
    raise InvalidIndentationError(msg,
                                  tokens.token_position(token),
                                  tokens.token_line(token),
                                  tokens.token_column(token))


class IndentationTokenStream:

    def __init__(self, _tokens, src, tokens_options):
        self.tokens = [token for token in _tokens]

        self.operator_tokens = tokens_options.get("operator_tokens", [])
        self.end_token = tokens_options["end_token"]
        self.end_expr_token = tokens_options["end_expr_token"]
        self.end_stream_token = tokens_options["end_stream_token"]
        self.new_line_token = tokens_options["new_line_token"]
        self.indent_token = tokens_options["indent_token"]

        if LOG_INDENTER:
            for token in self.tokens:
                print str(token)

        self.index = 0
        self.length = len(self.tokens)
        self.node = None
        self.token = None
        self.src = src
        self.logical_tokens = Fifo()
        self.produced_tokens = []

        level = self._find_level()
        self.layouts = plist.plist([Layout(-1, level, MODULE, None, None)])

    def create_end_token(self, token):

        return tokens.newtoken(self.end_token, "(end)",
                               tokens.token_position(token),
                               tokens.token_line(token),
                               tokens.token_column(token))

    def create_end_expression_token(self, token):
        return tokens.newtoken(self.end_expr_token, "(end_expr)",
                               tokens.token_position(token),
                               tokens.token_line(token),
                               tokens.token_column(token))

    def create_indent_token(self, token):
        return tokens.newtoken(self.indent_token, "(indent)",
                               tokens.token_position(token),
                               tokens.token_line(token),
                               tokens.token_column(token))

    def advanced_values(self):
        t = [tokens.token_value(token) for token in self.produced_tokens]
        return " ".join(t)

    def current_layout(self):
        return plist.head(self.layouts)

    def next_layout(self):
        return plist.head(plist.tail(self.layouts))

    def pop_layout(self):
        log("---- POP LAYOUT", self.current_layout())
        log(self.advanced_values())
        log(self.layouts)
        self.layouts = plist.tail(self.layouts)
        return self.current_layout()

    def _find_level(self):
        token = self._skip_newlines()
        return tokens.token_level(token)

    def _add_layout(self, node, type, level_tokens=None, terminators=None):
        token = nodes.node_token(node)
        cur = self.current_layout()
        level = tokens.token_level(token)
        layout = Layout(cur.level, level, type, level_tokens, terminators)

        log("---- ADD LAYOUT", layout)
        self.layouts = plist.cons(layout, self.layouts)

    def add_code_layout(self, node, terminators):
        # # support for f x y | x y -> 1 | x y -> 3
        # if self.current_layout().type == CODE:
        #     self.pop_layout()

        assert not self.current_layout().is_code()
        self._add_layout(node, CODE, terminators=terminators)

    def add_offside_layout(self, node):
        self._add_layout(node, OFFSIDE)

    def add_node_layout(self, node, level_tokens):
        self._add_layout(node, NODE, level_tokens=level_tokens)

    def add_free_code_layout(self, node, terminators):
        # TODO layouts in operators
        self._skip_newlines()
        self._add_layout(node, FREE, terminators=terminators)

    def has_layouts(self):
        return not plist.is_empty(self.layouts)

    def count_layouts(self):
        return plist.length(self.layouts)

    def has_tokens(self):
        return len(self.tokens) > 0

    def has_logic_tokens(self):
        return not self.logical_tokens.is_empty()

    def add_logical_token(self, token):
        log("=*=* ADD LOGICAL", token)
        self.logical_tokens.append(token)

    def next_logical(self):
        token = self.logical_tokens.pop()
        # log("=*=* NEXT LOGICAL TOKEN", str(token))
        return self.attach_token(token)

    def next_physical(self):
        token = self.tokens[self.index]
        # log( "++++ NEXT STREAM TOKEN", str(token))
        self.index += 1
        return token

    def _skip_newlines(self):
        token = self.next_physical()
        while tokens.token_type(token) == self.new_line_token:
            # log("++++ SKIP")
            token = self.next_physical()

        self.index -= 1
        return token

    def current_physical(self):
        return self.tokens[self.index]

    def current_type(self):
        return tokens.token_type(self.token)

    def current_physical_type(self):
        return tokens.token_type(self.current_physical())

    def _on_newline(self):
        token = self._skip_newlines()
        ttype = tokens.token_type(token)
        cur_type = self.current_type()

        layout = self.current_layout()
        level = tokens.token_level(token)
        log("----NEW LINE", level, layout, str(token))

        # TODO remove not layout.is_module() after implementing real pragmas
        # ![]
        if cur_type in self.operator_tokens and not layout.is_module():
            if level <= layout.level:
                return indentation_error("Indentation level of token next to"
                                         " operator must be bigger then"
                                         " of parent layout",
                                         token)

            return self.next_token()

        if layout.is_free() is True:
            return self.next_token()

        if level > layout.level:
            if ttype not in self.operator_tokens:
                self.add_logical_token(self.create_indent_token(token))

            return self.next_token()
        else:
            layouts = self.layouts
            while True:
                layout = plist.head(layouts)
                layouts = plist.tail(layouts)
                if layout is None:
                    return indentation_error(u"Indentation does not match"
                                             " with any of previous levels",
                                             token)

                if layout.level < level:
                    return indentation_error(u"Invalid indentation level",
                                             token)
                elif layout.level > level:
                    if layout.push_end_of_expression_on_new_line is True:
                        self.add_logical_token(
                            self.create_end_expression_token(token))
                    if layout.push_end_on_dedent is True:
                        self.add_logical_token(self.create_end_token(token))
                elif layout.level == level:
                    if layout.push_end_of_expression_on_new_line is True:
                        self.add_logical_token(
                            self.create_end_expression_token(token))
                    elif layout.is_node():
                        if ttype == self.end_token:
                            self.index += 1
                            self.add_logical_token(
                                self.create_end_token(token))
                            self.pop_layout()

                        elif not layout.has_level(ttype):
                            self.add_logical_token(
                                self.create_end_token(token))
                            self.add_logical_token(
                                self.create_end_expression_token(token))
                            self.pop_layout()
                    return self.next_token()

                log("---- POP_LAYOUT", layout)
                log(self.advanced_values())
                self.layouts = layouts

    def attach_token(self, token):
        log("^^^^^ATTACH", str(token))
        self.token = token
        self.node = nodes.node_blank(self.token)
        self.produced_tokens.append(self.token)
        return self.node

    def _on_end_token(self, token):
        layouts = self.layouts
        popped = []
        while True:
            layout = plist.head(layouts)
            layouts = plist.tail(layouts)
            if layout.is_node():
                log("---- POP NODE LAYOUT ON END TOKEN")
                log("POPPED LAYOUTS", popped)
                log(self.advanced_values())
                break
            elif layout.is_module():
                indentation_error(u"Invalid end keyword", token)
            else:
                popped.append(layout)
        self.layouts = layouts

    def next_token(self):
        if self.has_logic_tokens():
            return self.next_logical()

        if self.index >= self.length:
            return self.node

        token = self.next_physical()
        ttype = tokens.token_type(token)

        if ttype == self.new_line_token:
            return self._on_newline()

        elif ttype == self.end_token:
            self._on_end_token(token)
            return self.attach_token(token)
        elif ttype == self.end_stream_token:
            if not self.current_layout().is_module():
                indentation_error(u"Not all layouts closed", token)

        layout = self.current_layout()

        if layout.has_terminator(ttype):
            self.pop_layout()

        return self.attach_token(token)
