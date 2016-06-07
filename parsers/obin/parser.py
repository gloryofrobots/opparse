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
            return self.advance()
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


def set_literals(parser_builder):
    return (
        parser_builder
        .literal(lex.TT_INT)
        .literal(lex.TT_FLOAT)
        .literal(lex.TT_CHAR)
        .literal(lex.TT_STR)
        .literal(lex.TT_MULTI_STR)
        .literal(lex.TT_NAME)
        .literal(lex.TT_TRUE)
        .literal(lex.TT_FALSE)
        .literal(lex.TT_WILDCARD)
    )


def name_parser():
    return (
        set_literals(
            builder(break_on_juxtaposition=True, allow_unknown=True))

        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_INDENT)
        .symbol(lex.TT_CASE)
        .symbol(lex.TT_ASSIGN)
        .symbol(lex.TT_ELLIPSIS)
        .symbol(lex.TT_ENDSTREAM)

        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .symbol(lex.TT_OPERATOR, symbol_operator_name)
        .infix(lex.TT_DOT, 100, infix_name_pair)
    )


def type_parser():
    return (
        builder(juxtaposition_as_list=True, allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_END)
        .symbol(lex.TT_RCURLY)
        .prefix(lex.TT_LCURLY, prefix_lcurly_type, layout_lcurly)
        .prefix(lex.TT_NAME, prefix_name_as_symbol)
        .infix(lex.TT_COLON, 100, infix_name_pair)
        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
        .symbol(lex.TT_CASE, None)
    )


def method_signature_parser():
    return (
        builder(juxtaposition_as_list=True)
        .prefix(lex.TT_NAME, prefix_name_as_symbol)
        .symbol(lex.TT_DEF, None)
        .symbol(lex.TT_END, None)
        .symbol(lex.TT_ARROW, None)
        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    )


def import_names_parser():
    return (
        builder(allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_RPAREN, None)
        .symbol(lex.TT_COMMA, None)
        .literal(lex.TT_NAME)
        .infix(lex.TT_AS, 15, infix_name_pair)
        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    )


def import_parser():
    return (
        builder(allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_COMMA, None)
        .symbol(lex.TT_LPAREN, None)
        .symbol(lex.TT_HIDING, None)
        .symbol(lex.TT_HIDE, None)
        .symbol(lex.TT_IMPORT, None)
        .symbol(lex.TT_WILDCARD, None)
        .infix(lex.TT_DOT, 100, infix_name_pair)
        .infix(lex.TT_AS, 15, infix_name_pair)
        .literal(lex.TT_NAME)
    )


def guard_parser():
    return (
        set_literals(builder(allow_overloading=True))
        .symbol(lex.TT_COMMA, None)
        .symbol(lex.TT_RPAREN, None)
        .symbol(lex.TT_RCURLY, None)
        .symbol(lex.TT_RSQUARE, None)
        .symbol(lex.TT_ARROW, None)

        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)

        .infix(lex.TT_OR, 25, infix_led)
        .infix(lex.TT_AND, 30, infix_led)
        .infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_DOT, 100, infix_dot)
        .infix(lex.TT_COLON, 100, infix_name_pair)
    )


def setup_pattern_parser(parser_builder):
    return (
        set_literals(parser_builder)
        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix(lex.TT_LCURLY, prefix_lcurly_patterns, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_ELLIPSIS, prefix_nud)

        .infix(lex.TT_OF, 10, infix_led)
        .infix(lex.TT_AT_SIGN, 10, infix_at)
        .infix(lex.TT_DOUBLE_COLON, 60, infixr_led)
        .infix(lex.TT_COLON, 100, infix_name_pair)

        .symbol(lex.TT_WHEN)
        .symbol(lex.TT_CASE)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_RCURLY)
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ARROW)
        .symbol(lex.TT_ASSIGN)
    )


def pattern_parser():
    return setup_pattern_parser(builder())


def fun_pattern_parser():
    return (
        setup_pattern_parser(
            builder(break_on_juxtaposition=False,
                    juxtaposition_as_list=True))

        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    )


def fun_signature_parser():
    return (
        builder(juxtaposition_as_list=True)
        .literal(lex.TT_NAME)

        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_INDENT)
        .prefix(lex.TT_ELLIPSIS, prefix_nud)

        .infix(lex.TT_OF, 15, infix_led)
        .infix(lex.TT_COLON, 100, infix_name_pair)

        .literal(lex.TT_WILDCARD)
        .symbol(lex.TT_DEF)
        .symbol(lex.TT_ARROW)
        .symbol(lex.TT_CASE)
        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    )


def expression_parser():
    parser = (
        set_literals(builder(allow_overloading=True))
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ARROW)
        .symbol(lex.TT_THEN)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_RCURLY)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_END_EXPR)
        .symbol(lex.TT_AT_SIGN)
        .symbol(lex.TT_ELSE)
        .symbol(lex.TT_ELIF)
        .symbol(lex.TT_CASE)
        .symbol(lex.TT_THEN)
        .symbol(lex.TT_CATCH)
        .symbol(lex.TT_FINALLY)
        .symbol(lex.TT_WITH)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_END)
        .symbol(lex.TT_IN)

        .prefix(lex.TT_INDENT, prefix_indent)
        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_ELLIPSIS, prefix_nud)
        .prefix(lex.TT_IF, prefix_if)

        .prefix(lex.TT_FUN, prefix_fun)
        .prefix(lex.TT_LAMBDA, prefix_lambda)

        .prefix(lex.TT_MATCH, prefix_match)
        .prefix(lex.TT_TRY, prefix_try)
        .prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)
        .prefix(lex.TT_LET, prefix_let)

        .assignment(lex.TT_ASSIGN, 10)
        .infix(lex.TT_OF, 15, infix_led)
        .infix(lex.TT_OR, 25, infix_led)
        .infix(lex.TT_AND, 30, infix_led)
        .infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
        .infix(lex.TT_DOUBLE_COLON, 70, infixr_led)

        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_COLON, 100, infix_name_pair)
        .infix(lex.TT_DOT, 100, infix_dot)

        .infix(lex.TT_INFIX_DOT_LCURLY, 100, infix_lcurly)
        .infix(lex.TT_INFIX_DOT_LSQUARE, 100, infix_lsquare)
        .infix(lex.TT_INFIX_DOT_LPAREN, 100, infix_lparen)
        .stmt(lex.TT_THROW, prefix_throw)
        .build("expression_parser")
    )

    return (
        parser
        .add_builder("pattern_parser", pattern_parser())
        .add_builder("guard_parser", guard_parser())
        .add_builder("fun_pattern_parser", fun_pattern_parser())
        .add_builder("fun_signature_parser", fun_signature_parser())
        .add_builder("guard_parser", guard_parser())
        .add_builder("name_parser", name_parser())
    )

    return parser


def obin_parser():
    parser = (
        set_literals(
            builder(allow_overloading=True)
        )
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ARROW)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_RCURLY)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_END)
        .symbol(lex.TT_END_EXPR)
        .symbol(lex.TT_ENDSTREAM)

        .prefix(lex.TT_INDENT, prefix_indent)
        .prefix(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_LAMBDA, prefix_lambda)

        .assignment(lex.TT_ASSIGN, 10)
        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_DOT, 100, infix_dot)
        .infix(lex.TT_COLON, 100, infix_name_pair)

        .stmt(lex.TT_FUN, prefix_module_fun)
        .stmt(lex.TT_TRAIT, stmt_trait)
        .stmt(lex.TT_TYPE, stmt_type)
        .stmt(lex.TT_IMPLEMENT, stmt_implement)
        .stmt(lex.TT_EXTEND, stmt_extend)
        .stmt(lex.TT_IMPORT, stmt_import)
        .stmt(lex.TT_FROM, stmt_from)
        .stmt(lex.TT_EXPORT, stmt_export)
        .stmt(lex.TT_INFIXL, stmt_infixl)
        .stmt(lex.TT_INFIXR, stmt_infixr)
        .stmt(lex.TT_PREFIX, stmt_prefix)
        .build("obin_parser")
    )

    return (
        parser
        .add_builder("import_parser", import_parser())
        .add_builder("pattern_parser", pattern_parser())
        .add_builder("guard_parser", guard_parser())
        .add_builder("fun_pattern_parser", fun_pattern_parser())
        .add_builder("fun_signature_parser", fun_signature_parser())
        .add_builder("name_parser", name_parser())
        .add_builder("import_names_parser", import_names_parser())
        .add_builder("type_parser", type_parser())
        .add_builder("method_signature_parser", method_signature_parser())
        .add_subparser(expression_parser())
    )


def parse(source):
    parser = obin_parser()
    ts = create_stream(parser, source)
    return parse_token_stream(parser, ts)
