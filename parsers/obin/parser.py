from lexicon import ObinLexicon
from opparse.indenter import IndentationTokenStream
from callbacks import *

lex = ObinLexicon()


def create_stream(parser, source):
    indenter_settings = dict(
        operator_tokens=[lex.TT_DOUBLE_COLON,
                         parser.lex.TT_COLON, lex.TT_OPERATOR,
                         parser.lex.TT_DOT,
                         lex.TT_ASSIGN, lex.TT_OR, lex.TT_AND],

        end_expr_token=lex.TT_END_EXPR,
        indent_token=lex.TT_INDENT,
        end_token=parser.lex.TT_END,
        end_stream_token=parser.lex.TT_ENDSTREAM,
        new_line_token=parser.lex.TT_NEWLINE
    )

    lx = lexer.lexer(source, parser.lex)
    tokens_iter = lx.tokens()
    return IndentationTokenStream(tokens_iter, source, indenter_settings)


class ObinParser(Parser):
    def on_endofexpression(self):
        if self.isend():
            return None
        if self.token_type in TERM_BLOCK:
            return self.node
        if self.token_type == self.lex.TT_END_EXPR:
            return advance(self)
        return False

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
            flatten = flatten_juxtaposition(self, node)
            # probably overkill
            if len(flatten) < 2:
                parse_error(self,
                            "Invalid use of juxtaposition operator", node)

            if self.juxtaposition_as_list:
                return self.postprocess(flatten)
            else:
                caller = plist.head(flatten)
                args = plist.tail(flatten)
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
            return nodes.Node(node.node_type,
                                 node.token, children)


def create_parser():
    parser = ObinParser(lex, allow_overloading=True)
    set_parser_literals(parser)

    parser.add_subparser("import_parser",
                         import_parser_init(ObinParser(lex, allow_unknown=True)))
    parser.add_subparser("pattern_parser", pattern_parser_init(ObinParser(lex, )))
    parser.add_subparser("guard_parser",
                         guard_parser_init(ObinParser(lex, allow_overloading=True)))
    parser.add_subparser("fun_pattern_parser",
                         fun_pattern_parser_init(
                             ObinParser(lex, break_on_juxtaposition=False,
                                        juxtaposition_as_list=True)))

    parser.add_subparser("fun_signature_parser",
                         fun_signature_parser_init(
                             ObinParser(lex, juxtaposition_as_list=True)))

    parser.add_subparser("guard_parser",
                         guard_parser_init(ObinParser(lex, allow_overloading=True)))

    parser.add_subparser("expression_parser",
                         expression_parser_init(
                             ObinParser(lex, allow_overloading=True)))

    parser.add_subparser("name_parser", name_parser_init(ObinParser(lex,
                                                                    break_on_juxtaposition=True, allow_unknown=True)))

    parser.add_subparser("import_names_parser",
                         import_names_parser_init(
                             ObinParser(lex, allow_unknown=True)))

    parser.add_subparser("type_parser",
                         type_parser_init(
                             ObinParser(lex, juxtaposition_as_list=True,
                                        allow_unknown=True)))

    parser.add_subparser("method_signature_parser",
                         method_signature_parser_init(
                             ObinParser(lex, juxtaposition_as_list=True)))

    symbol(parser, lex.TT_RSQUARE)
    symbol(parser, lex.TT_ARROW)
    symbol(parser, lex.TT_RPAREN)
    symbol(parser, lex.TT_RCURLY)
    symbol(parser, lex.TT_COMMA)
    symbol(parser, lex.TT_END)
    symbol(parser, lex.TT_END_EXPR)
    symbol(parser, lex.TT_ENDSTREAM)

    prefix(parser, lex.TT_INDENT, prefix_indent)
    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, lex.TT_SHARP, prefix_sharp)
    prefix(parser, lex.TT_LAMBDA, prefix_lambda)

    assignment(parser, lex.TT_ASSIGN, 10)
    infix(parser, lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, lex.TT_DOT, 100, infix_dot)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)

    stmt(parser, lex.TT_FUN, prefix_module_fun)
    stmt(parser, lex.TT_TRAIT, stmt_trait)
    stmt(parser, lex.TT_TYPE, stmt_type)
    stmt(parser, lex.TT_IMPLEMENT, stmt_implement)
    stmt(parser, lex.TT_EXTEND, stmt_extend)
    stmt(parser, lex.TT_IMPORT, stmt_import)
    stmt(parser, lex.TT_FROM, stmt_from)
    stmt(parser, lex.TT_EXPORT, stmt_export)
    # stmt(parser, lex.TT_MODULE, stmt_module)
    stmt(parser, lex.TT_INFIXL, stmt_infixl)
    stmt(parser, lex.TT_INFIXR, stmt_infixr)
    stmt(parser, lex.TT_PREFIX, stmt_prefix)
    return parser


def name_parser_init(parser):
    symbol(parser, lex.TT_COMMA, None)
    symbol(parser, lex.TT_UNKNOWN, None)
    # symbol(parser, lex.TT_WILDCARD, None)
    symbol(parser, lex.TT_RPAREN, None)
    symbol(parser, lex.TT_INDENT, None)
    set_parser_literals(parser)
    symbol(parser, lex.TT_CASE, None)
    symbol(parser, lex.TT_ASSIGN, None)
    symbol(parser, lex.TT_ELLIPSIS, None)
    symbol(parser, lex.TT_ENDSTREAM)

    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    symbol(parser, lex.TT_OPERATOR, symbol_operator_name)
    infix(parser, lex.TT_DOT, 100, infix_name_pair)
    return parser


def type_parser_init(parser):
    # parser.break_on_juxtaposition = True
    symbol(parser, lex.TT_UNKNOWN)
    # literal(parser, lex.TT_TYPENAME)
    symbol(parser, lex.TT_COMMA)
    symbol(parser, lex.TT_END)
    symbol(parser, lex.TT_RCURLY)
    prefix(parser, lex.TT_LCURLY, prefix_lcurly_type, layout_lcurly)
    prefix(parser, lex.TT_NAME, prefix_name_as_symbol)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)
    # infix(parser, lex.TT_CASE, 15, led_infixr)
    # infix(parser, lex.TT_ASSIGN, 10, led_infixr)
    infix(parser, lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    symbol(parser, lex.TT_CASE, None)
    return parser


def method_signature_parser_init(parser):
    prefix(parser, lex.TT_NAME, prefix_name_as_symbol)
    symbol(parser, lex.TT_DEF, None)
    symbol(parser, lex.TT_END, None)
    symbol(parser, lex.TT_ARROW, None)
    infix(parser, lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return parser


def import_names_parser_init(parser):
    symbol(parser, lex.TT_UNKNOWN)
    symbol(parser, lex.TT_RPAREN, None)
    symbol(parser, lex.TT_COMMA, None)
    literal(parser, lex.TT_NAME)
    infix(parser, lex.TT_AS, 15, infix_name_pair)
    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    return parser


def import_parser_init(parser):
    symbol(parser, lex.TT_UNKNOWN)
    symbol(parser, lex.TT_COMMA, None)
    symbol(parser, lex.TT_LPAREN, None)
    symbol(parser, lex.TT_HIDING, None)
    symbol(parser, lex.TT_HIDE, None)
    symbol(parser, lex.TT_IMPORT, None)
    symbol(parser, lex.TT_WILDCARD, None)
    infix(parser, lex.TT_DOT, 100, infix_name_pair)
    infix(parser, lex.TT_AS, 15, infix_name_pair)
    literal(parser, lex.TT_NAME)

    return parser


def guard_parser_init(parser):
    parser = set_parser_literals(parser)

    symbol(parser, lex.TT_COMMA, None)
    symbol(parser, lex.TT_RPAREN, None)
    symbol(parser, lex.TT_RCURLY, None)
    symbol(parser, lex.TT_RSQUARE, None)
    symbol(parser, lex.TT_ARROW, None)

    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, lex.TT_SHARP, prefix_sharp)
    prefix(parser, lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)

    infix(parser, lex.TT_OR, 25, led_infix)
    infix(parser, lex.TT_AND, 30, led_infix)
    infix(parser, lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
    infix(parser, lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, lex.TT_DOT, 100, infix_dot)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)
    return parser


def pattern_parser_init(parser):
    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, lex.TT_LCURLY, prefix_lcurly_patterns, layout_lcurly)
    prefix(parser, lex.TT_SHARP, prefix_sharp)
    prefix(parser, lex.TT_ELLIPSIS, prefix_nud)

    infix(parser, lex.TT_OF, 10, led_infix)
    infix(parser, lex.TT_AT_SIGN, 10, infix_at)
    infix(parser, lex.TT_DOUBLE_COLON, 60, led_infixr)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)

    symbol(parser, lex.TT_WHEN)
    symbol(parser, lex.TT_CASE)
    symbol(parser, lex.TT_COMMA)
    symbol(parser, lex.TT_RPAREN)
    symbol(parser, lex.TT_RCURLY)
    symbol(parser, lex.TT_RSQUARE)
    symbol(parser, lex.TT_ARROW)
    symbol(parser, lex.TT_ASSIGN)

    parser = set_parser_literals(parser)
    return parser


def fun_pattern_parser_init(parser):
    parser = pattern_parser_init(parser)
    infix(parser, lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return parser


def fun_signature_parser_init(parser):
    literal(parser, lex.TT_NAME)

    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    symbol(parser, lex.TT_RPAREN)
    symbol(parser, lex.TT_INDENT)
    prefix(parser, lex.TT_ELLIPSIS, prefix_nud)

    infix(parser, lex.TT_OF, 15, led_infix)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)

    literal(parser, lex.TT_WILDCARD)
    symbol(parser, lex.TT_DEF)
    symbol(parser, lex.TT_ARROW)
    symbol(parser, lex.TT_CASE)
    infix(parser, lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return parser


def set_parser_literals(parser):
    literal(parser, lex.TT_INT)
    literal(parser, lex.TT_FLOAT)
    literal(parser, lex.TT_CHAR)
    literal(parser, lex.TT_STR)
    literal(parser, lex.TT_MULTI_STR)
    literal(parser, lex.TT_NAME)
    literal(parser, lex.TT_TRUE)
    literal(parser, lex.TT_FALSE)
    literal(parser, lex.TT_WILDCARD)
    return parser


def expression_parser_init(parser):
    parser = set_parser_literals(parser)

    parser.add_subparser("pattern_parser",
                         pattern_parser_init(ObinParser(lex)))

    parser.add_subparser("guard_parser",
                         guard_parser_init(ObinParser(lex, allow_overloading=True)))

    parser.add_subparser("fun_pattern_parser",
                         fun_pattern_parser_init(
                             ObinParser(lex, break_on_juxtaposition=False,
                                        juxtaposition_as_list=True)))

    parser.add_subparser("fun_signature_parser",
                         fun_signature_parser_init(
                             ObinParser(lex, juxtaposition_as_list=True)))

    parser.add_subparser("guard_parser",
                         guard_parser_init(ObinParser(lex,
                                                      allow_overloading=True)))

    parser.add_subparser("name_parser",
                         name_parser_init(ObinParser(lex,
                                                     break_on_juxtaposition=True,
                                                     allow_unknown=True)))

    symbol(parser, lex.TT_RSQUARE)
    symbol(parser, lex.TT_ARROW)
    symbol(parser, lex.TT_THEN)
    symbol(parser, lex.TT_RPAREN)
    symbol(parser, lex.TT_RCURLY)
    symbol(parser, lex.TT_COMMA)
    symbol(parser, lex.TT_END_EXPR)
    symbol(parser, lex.TT_AT_SIGN)
    symbol(parser, lex.TT_ELSE)
    symbol(parser, lex.TT_ELIF)
    symbol(parser, lex.TT_CASE)
    symbol(parser, lex.TT_THEN)
    symbol(parser, lex.TT_CATCH)
    symbol(parser, lex.TT_FINALLY)
    symbol(parser, lex.TT_WITH)
    symbol(parser, lex.TT_COMMA)
    symbol(parser, lex.TT_END)
    symbol(parser, lex.TT_IN)

    prefix(parser, lex.TT_INDENT, prefix_indent)
    prefix(parser, lex.TT_LPAREN, prefix_lparen, layout_lparen)
    prefix(parser, lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    prefix(parser, lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    prefix(parser, lex.TT_SHARP, prefix_sharp)
    prefix(parser, lex.TT_ELLIPSIS, prefix_nud)
    prefix(parser, lex.TT_IF, prefix_if)

    prefix(parser, lex.TT_FUN, prefix_fun)
    prefix(parser, lex.TT_LAMBDA, prefix_lambda)

    prefix(parser, lex.TT_MATCH, prefix_match)
    prefix(parser, lex.TT_TRY, prefix_try)
    prefix(parser, lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)
    prefix(parser, lex.TT_LET, prefix_let)

    assignment(parser, lex.TT_ASSIGN, 10)
    infix(parser, lex.TT_OF, 15, led_infix)
    infix(parser, lex.TT_OR, 25, led_infix)
    infix(parser, lex.TT_AND, 30, led_infix)
    infix(parser, lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
    infix(parser, lex.TT_DOUBLE_COLON, 70, led_infixr)

    infix(parser, lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, lex.TT_COLON, 100, infix_name_pair)
    infix(parser, lex.TT_DOT, 100, infix_dot)

    infix(parser, lex.TT_INFIX_DOT_LCURLY, 100, infix_lcurly)
    infix(parser, lex.TT_INFIX_DOT_LSQUARE, 100, infix_lsquare)
    infix(parser, lex.TT_INFIX_DOT_LPAREN, 100, infix_lparen)

    stmt(parser, lex.TT_THROW, prefix_throw)
    return parser


def parse(source):
    parser = create_parser()
    ts = create_stream(parser, source)
    return parse_token_stream(parser, ts)
