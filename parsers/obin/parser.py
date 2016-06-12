from lexicon import ObinLexicon
from opparse.indenter import IndentationTokenStream
from callbacks import *

lex = ObinLexicon()


def create_stream(parser, source):
    indenter_settings = dict(
        operator_tokens=[lex.TT_DOUBLE_COLON,
                         lex.TT_COLON, lex.TT_OPERATOR,
                         lex.TT_DOT,
                         lex.TT_ASSIGN, lex.TT_OR, lex.TT_AND],

        end_expr_token=lex.TT_END_EXPR,
        indent_token=lex.TT_INDENT,
        end_token=lex.TT_END,
        end_stream_token=lex.TT_ENDSTREAM,
        new_line_token=lex.TT_NEWLINE
    )

    lx = lexer.Lexer(parser.lex, source)
    return IndentationTokenStream(lx.as_list(), source, indenter_settings)


class ObinParser(JuxtapositionParser):

    def advance_end(self):
        self.advance_expected(self.lex.TT_END)

    def endofexpression(self):
        if self.isend():
            return False
        if self.token_type in self.lex.TERM_BLOCK:
            return True
        if self.token_type == self.lex.TT_END_EXPR:
            self.advance()
            return True
        return False


def builder(**settings):
    return ObinParser.builder(lex, settings)


def set_literals(parser_builder):
    return (
        parser_builder
        .literal(lex.TT_INT, lex.NT_INT)
        .literal(lex.TT_FLOAT, lex.NT_FLOAT)
        .literal(lex.TT_CHAR, lex.NT_CHAR)
        .literal(lex.TT_STR, lex.NT_STR)
        .literal(lex.TT_MULTI_STR, lex.NT_MULTI_STR)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .literal(lex.TT_TRUE, lex.NT_TRUE)
        .literal(lex.TT_FALSE, lex.NT_FALSE)
        .literal(lex.TT_WILDCARD, lex.NT_WILDCARD)
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

        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout=layout_lparen)
        .symbol(lex.TT_OPERATOR, symbol_operator_name)
        .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_LOOKUP)
    )


def type_parser():
    return (
        builder(juxtaposition_as_list=True, allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_END)
        .symbol(lex.TT_RCURLY)
        .prefix_layout(lex.TT_LCURLY, prefix_lcurly_type, layout_lcurly)
        .prefix(lex.TT_NAME, prefix_name_as_symbol)
        .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_LOOKUP)
        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
        .symbol(lex.TT_CASE)
    )


def method_signature_parser():
    return (
        builder(juxtaposition_as_list=True)
        .prefix(lex.TT_NAME, prefix_name_as_symbol)
        .symbol(lex.TT_DEF)
        .symbol(lex.TT_END)
        .symbol(lex.TT_ARROW)
        .infix(lex.TT_JUXTAPOSITION, 5, infix_juxtaposition)
    )


def import_names_parser():
    return (
        builder(allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_COMMA)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .infix(lex.TT_AS, 15, infix_name_pair, lex.NT_AS)
        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
    )


def import_parser():
    return (
        builder(allow_unknown=True)
        .symbol(lex.TT_UNKNOWN)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_LPAREN)
        .symbol(lex.TT_HIDING)
        .symbol(lex.TT_HIDE)
        .symbol(lex.TT_IMPORT)
        .symbol(lex.TT_WILDCARD)
        .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_LOOKUP)
        .infix(lex.TT_AS, 15, infix_name_pair, lex.NT_AS)
        .literal(lex.TT_NAME, lex.NT_NAME)
    )


def guard_parser():
    return (
        set_literals(builder(allow_overloading=True))
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_RCURLY)
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ARROW)

        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix_layout(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix_layout(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)

        .infix_default(lex.TT_OR, 25, lex.NT_OR)
        .infix_default(lex.TT_AND, 30, lex.NT_AND)
        .infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)
        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_DOT, 100, infix_dot, lex.NT_LOOKUP)
    )


def setup_pattern_parser(parser_builder):
    return (
        set_literals(parser_builder)
        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix_layout(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix_layout(lex.TT_LCURLY, prefix_lcurly_patterns, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix_default(lex.TT_ELLIPSIS, lex.NT_REST)

        .infix_default(lex.TT_OF, 10, lex.NT_OF)
        .infix(lex.TT_AT_SIGN, 10, infix_at)
        .infixr(lex.TT_DOUBLE_COLON, 60, lex.NT_CONS)

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
        .literal(lex.TT_NAME, lex.NT_NAME)

        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_INDENT)
        .prefix_default(lex.TT_ELLIPSIS, lex.NT_REST)

        .infix_default(lex.TT_OF, 15, lex.NT_OF)
        .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_LOOKUP)

        .literal(lex.TT_WILDCARD, lex.NT_WILDCARD)
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
        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix_layout(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix_layout(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix_default(lex.TT_ELLIPSIS, lex.NT_REST)
        .prefix(lex.TT_IF, prefix_if)

        .prefix(lex.TT_FUN, prefix_fun)
        .prefix(lex.TT_LAMBDA, prefix_lambda)

        .prefix(lex.TT_MATCH, prefix_match)
        .prefix(lex.TT_TRY, prefix_try)
        .prefix(lex.TT_BACKTICK_OPERATOR, prefix_backtick_operator)
        .prefix(lex.TT_LET, prefix_let)

        .assignment(lex.TT_ASSIGN, 10, lex.NT_ASSIGN)
        .infix_default(lex.TT_OF, 15, lex.NT_OF)
        .infix_default(lex.TT_OR, 25, lex.NT_OR)
        .infix_default(lex.TT_AND, 30, lex.NT_AND)
        .infixr(lex.TT_DOUBLE_COLON, 70, lex.NT_CONS)
        .infix(lex.TT_BACKTICK_NAME, 35, infix_backtick_name)

        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_DOT, 100, infix_dot, lex.NT_LOOKUP)

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
        .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
        .prefix_layout(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
        .prefix_layout(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
        .prefix(lex.TT_SHARP, prefix_sharp)
        .prefix(lex.TT_LAMBDA, prefix_lambda)

        .assignment(lex.TT_ASSIGN, 10, lex.NT_ASSIGN)
        .infix(lex.TT_JUXTAPOSITION, 90, infix_juxtaposition)
        .infix(lex.TT_DOT, 100, infix_dot)

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
