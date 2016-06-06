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


def builder(**settings):
    return Builder(lex, settings, ObinParser)


def set_literals(b):
    b.literal(lex.TT_INT)
    b.literal(lex.TT_FLOAT)
    b.literal(lex.TT_CHAR)
    b.literal(lex.TT_STR)
    b.literal(lex.TT_MULTI_STR)
    b.literal(lex.TT_NAME)
    b.literal(lex.TT_TRUE)
    b.literal(lex.TT_FALSE)
    b.literal(lex.TT_WILDCARD)
    return b


def name_parser():
    b = builder(break_on_juxtaposition=True, allow_unknown=True)
    set_literals(b)
    b.symbol(lex.TT_COMMA, None)
    b.symbol(lex.TT_UNKNOWN, None)
    # symbol(parser, lex.TT_WILDCARD, None)
    b.symbol(lex.TT_RPAREN, None)
    b.symbol(lex.TT_INDENT, None)
    b.symbol(lex.TT_CASE, None)
    b.symbol(lex.TT_ASSIGN, None)
    b.symbol(lex.TT_ELLIPSIS, None)
    b.symbol(lex.TT_ENDSTREAM)

    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.symbol(lex.TT_OPERATOR, symbol_operator_name)
    b.infix(lex.TT_DOT, 100, infix_name_pair)
    return b


def type_parser():
    b = builder(juxtaposition_as_list=True, allow_unknown=True)
    b.symbol(lex.TT_UNKNOWN)
    b.symbol(lex.TT_COMMA)
    b.symbol(lex.TT_END)
    b.symbol(lex.TT_RCURLY)
    b.prefix(lex.TT_LCURLY, prefix_lcurly_type, layout_lcurly)
    b.prefix(lex.TT_NAME, prefix_name_as_symbol)
    b.infix(lex.TT_COLON, 100, infix_name_pair)
    b.infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    b.symbol(lex.TT_CASE, None)
    return b


def method_signature_parser():
    b = builder(juxtaposition_as_list=True)
    b.prefix(lex.TT_NAME, prefix_name_as_symbol)
    b.symbol(lex.TT_DEF, None)
    b.symbol(lex.TT_END, None)
    b.symbol(lex.TT_ARROW, None)
    b.infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return b


def import_names_parser():
    b = builder(allow_unknown=True)
    b.symbol(lex.TT_UNKNOWN)
    b.symbol(lex.TT_RPAREN, None)
    b.symbol(lex.TT_COMMA, None)
    b.literal(lex.TT_NAME)
    b.infix(lex.TT_AS, 15, infix_name_pair)
    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    return b


def import_parser():
    b = builder(allow_unknown=True)
    b.symbol(lex.TT_UNKNOWN)
    b.symbol(lex.TT_COMMA, None)
    b.symbol(lex.TT_LPAREN, None)
    b.symbol(lex.TT_HIDING, None)
    b.symbol(lex.TT_HIDE, None)
    b.symbol(lex.TT_IMPORT, None)
    b.symbol(lex.TT_WILDCARD, None)
    b.infix(lex.TT_DOT, 100, infix_name_pair)
    b.infix(lex.TT_AS, 15, infix_name_pair)
    b.literal(lex.TT_NAME)

    return b


def guard_parser():
    b = builder(allow_overloading=True)
    set_literals(b)

    b.symbol(lex.TT_COMMA, None)
    b.symbol(lex.TT_RPAREN, None)
    b.symbol(lex.TT_RCURLY, None)
    b.symbol(lex.TT_RSQUARE, None)
    b.symbol(lex.TT_ARROW, None)

    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    b.prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    b.prefix(lex.TT_SHARP, prefix_sharp)
    b.prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)

    b.infix(lex.TT_OR, 25, led_infix)
    b.infix(lex.TT_AND, 30, led_infix)
    b.infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
    b.infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    b.infix(lex.TT_DOT, 100, infix_dot)
    b.infix(lex.TT_COLON, 100, infix_name_pair)
    return b


def setup_pattern_parser(b):
    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    b.prefix(lex.TT_LCURLY, prefix_lcurly_patterns, layout_lcurly)
    b.prefix(lex.TT_SHARP, prefix_sharp)
    b.prefix(lex.TT_ELLIPSIS, prefix_nud)

    b.infix(lex.TT_OF, 10, led_infix)
    b.infix(lex.TT_AT_SIGN, 10, infix_at)
    b.infix(lex.TT_DOUBLE_COLON, 60, led_infixr)
    b.infix(lex.TT_COLON, 100, infix_name_pair)

    b.symbol(lex.TT_WHEN)
    b.symbol(lex.TT_CASE)
    b.symbol(lex.TT_COMMA)
    b.symbol(lex.TT_RPAREN)
    b.symbol(lex.TT_RCURLY)
    b.symbol(lex.TT_RSQUARE)
    b.symbol(lex.TT_ARROW)
    b.symbol(lex.TT_ASSIGN)

    set_literals(b)
    return b


def pattern_parser():
    return setup_pattern_parser(builder())


def fun_pattern_parser():
    b = builder(break_on_juxtaposition=False, juxtaposition_as_list=True)
    setup_pattern_parser(b)
    b.infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return b


def fun_signature_parser():
    b = builder(juxtaposition_as_list=True)
    b.literal(lex.TT_NAME)

    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.symbol(lex.TT_RPAREN)
    b.symbol(lex.TT_INDENT)
    b.prefix(lex.TT_ELLIPSIS, prefix_nud)

    b.infix(lex.TT_OF, 15, led_infix)
    b.infix(lex.TT_COLON, 100, infix_name_pair)

    b.literal(lex.TT_WILDCARD)
    b.symbol(lex.TT_DEF)
    b.symbol(lex.TT_ARROW)
    b.symbol(lex.TT_CASE)
    b.infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    return b


def expression_parser():
    b = builder(allow_overloading=True)
    set_literals(b)
    b.symbol(lex.TT_RSQUARE)
    b.symbol(lex.TT_ARROW)
    b.symbol(lex.TT_THEN)
    b.symbol(lex.TT_RPAREN)
    b.symbol(lex.TT_RCURLY)
    b.symbol(lex.TT_COMMA)
    b.symbol(lex.TT_END_EXPR)
    b.symbol(lex.TT_AT_SIGN)
    b.symbol(lex.TT_ELSE)
    b.symbol(lex.TT_ELIF)
    b.symbol(lex.TT_CASE)
    b.symbol(lex.TT_THEN)
    b.symbol(lex.TT_CATCH)
    b.symbol(lex.TT_FINALLY)
    b.symbol(lex.TT_WITH)
    b.symbol(lex.TT_COMMA)
    b.symbol(lex.TT_END)
    b.symbol(lex.TT_IN)

    b.prefix(lex.TT_INDENT, prefix_indent)
    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    b.prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    b.prefix(lex.TT_SHARP, prefix_sharp)
    b.prefix(lex.TT_ELLIPSIS, prefix_nud)
    b.prefix(lex.TT_IF, prefix_if)

    b.prefix(lex.TT_FUN, prefix_fun)
    b.prefix(lex.TT_LAMBDA, prefix_lambda)

    b.prefix(lex.TT_MATCH, prefix_match)
    b.prefix(lex.TT_TRY, prefix_try)
    b.prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)
    b.prefix(lex.TT_LET, prefix_let)

    b.assignment(lex.TT_ASSIGN, 10)
    b.infix(lex.TT_OF, 15, led_infix)
    b.infix(lex.TT_OR, 25, led_infix)
    b.infix(lex.TT_AND, 30, led_infix)
    b.infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
    b.infix(lex.TT_DOUBLE_COLON, 70, led_infixr)

    b.infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    b.infix(lex.TT_COLON, 100, infix_name_pair)
    b.infix(lex.TT_DOT, 100, infix_dot)

    b.infix(lex.TT_INFIX_DOT_LCURLY, 100, infix_lcurly)
    b.infix(lex.TT_INFIX_DOT_LSQUARE, 100, infix_lsquare)
    b.infix(lex.TT_INFIX_DOT_LPAREN, 100, infix_lparen)

    b.stmt(lex.TT_THROW, prefix_throw)

    parser = b.build("expression_parser")

    parser.add_builder("pattern_parser", pattern_parser())

    parser.add_builder("guard_parser", guard_parser())

    parser.add_builder("fun_pattern_parser", fun_pattern_parser())

    parser.add_builder("fun_signature_parser", fun_signature_parser())

    parser.add_builder("guard_parser", guard_parser())

    parser.add_builder("name_parser", name_parser())

    return parser


def obin_parser():
    b = builder(allow_overloading=True)
    set_literals(b)

    b.symbol(lex.TT_RSQUARE)
    b.symbol(lex.TT_ARROW)
    b.symbol(lex.TT_RPAREN)
    b.symbol(lex.TT_RCURLY)
    b.symbol(lex.TT_COMMA)
    b.symbol(lex.TT_END)
    b.symbol(lex.TT_END_EXPR)
    b.symbol(lex.TT_ENDSTREAM)

    b.prefix(lex.TT_INDENT, prefix_indent)
    b.prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    b.prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
    b.prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
    b.prefix(lex.TT_SHARP, prefix_sharp)
    b.prefix(lex.TT_LAMBDA, prefix_lambda)

    b.assignment(lex.TT_ASSIGN, 10)
    b.infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
    b.infix(lex.TT_DOT, 100, infix_dot)
    b.infix(lex.TT_COLON, 100, infix_name_pair)

    b.stmt(lex.TT_FUN, prefix_module_fun)
    b.stmt(lex.TT_TRAIT, stmt_trait)
    b.stmt(lex.TT_TYPE, stmt_type)
    b.stmt(lex.TT_IMPLEMENT, stmt_implement)
    b.stmt(lex.TT_EXTEND, stmt_extend)
    b.stmt(lex.TT_IMPORT, stmt_import)
    b.stmt(lex.TT_FROM, stmt_from)
    b.stmt(lex.TT_EXPORT, stmt_export)
    # stmt(parser, lex.TT_MODULE, stmt_module)
    b.stmt(lex.TT_INFIXL, stmt_infixl)
    b.stmt(lex.TT_INFIXR, stmt_infixr)
    b.stmt(lex.TT_PREFIX, stmt_prefix)

    parser = b.build("obin_parser")

    parser.add_builder("import_parser", import_parser())

    parser.add_builder("pattern_parser", pattern_parser())

    parser.add_builder("guard_parser", guard_parser())

    parser.add_builder("fun_pattern_parser", fun_pattern_parser())

    parser.add_builder("fun_signature_parser", fun_signature_parser())

    parser.add_builder("name_parser", name_parser())

    parser.add_builder("import_names_parser", import_names_parser())

    parser.add_builder("type_parser", type_parser())

    parser.add_builder("method_signature_parser", method_signature_parser())

    parser.add_subparser(expression_parser())
    return parser


def parse(source):
    parser = obin_parser()
    ts = create_stream(parser, source)
    return parse_token_stream(parser, ts)
