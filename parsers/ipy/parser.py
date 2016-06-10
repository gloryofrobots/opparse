import lexicon
from opparse.indenter import IndentationTokenStream
from callbacks import *

lex = lexicon.IpyLexicon()


def create_stream(parser, source):
    indenter_settings = dict(
        operator_tokens=[lex.TT_PLUS, lex.TT_MINUS, lex.TT_STAR, lex.TT_SLASH,
                         lex.TT_MINUS_ASSIGN, lex.TT_PLUS_ASSIGN, lex.TT_ASSIGN,
                         lex.TT_DOT, lex.TT_OR, lex.TT_AND],

        end_expr_token=lex.TT_END_EXPR,
        indent_token=lex.TT_INDENT,
        end_token=lex.TT_END,
        end_stream_token=lex.TT_ENDSTREAM,
        new_line_token=lex.TT_NEWLINE
    )

    lx = lexer.Lexer(parser.lex, source)
    return IndentationTokenStream(lx.as_list(), source, indenter_settings)


class IpyParser(Parser):
    def advance_end(self):
        self.advance_expected_one_of(self.lex.TERM_BLOCK)

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
    return Builder(lex, settings, IpyParser)


def set_literals(parser_builder):
    return (
        parser_builder
            .literal(lex.TT_INT, lex.NT_INT)
            .literal(lex.TT_STR, lex.NT_STR)
            .literal(lex.TT_NAME, lex.NT_NAME)
            .literal(lex.TT_TRUE, lex.NT_TRUE)
            .literal(lex.TT_FALSE, lex.NT_FALSE)
            .literal(lex.TT_NONE, lex.NT_NONE)
    )


def name_parser():
    return (
        builder(allow_unknown=True)
            .literal(lex.TT_NAME, lex.NT_NAME)
            .symbol(lex.TT_COMMA)
            .symbol(lex.TT_UNKNOWN)
            .symbol(lex.TT_RPAREN)
            .symbol(lex.TT_INDENT)
            .symbol(lex.TT_COLON)
            .symbol(lex.TT_ENDSTREAM)

            .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
            .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_DOT)
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


def exception_name_parser():
    return (
        builder(allow_unknown=True)
            .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_DOT)
            .infix(lex.TT_AS, 15, infix_name_pair, lex.NT_AS)
            .literal(lex.TT_NAME, lex.NT_NAME)
    )


def import_parser():
    return (
        builder(allow_unknown=True)
            .symbol(lex.TT_UNKNOWN)
            .symbol(lex.TT_COMMA)
            .symbol(lex.TT_LPAREN)
            .symbol(lex.TT_IMPORT)
            .symbol(lex.TT_STAR)
            .infix(lex.TT_DOT, 100, infix_name_pair, lex.NT_DOT)
            .infix(lex.TT_AS, 15, infix_name_pair, lex.NT_AS)
            .literal(lex.TT_NAME, lex.NT_NAME)
    )


def signature_parser():
    return (
        builder()
            .symbol(lex.TT_RPAREN)
            .symbol(lex.TT_INDENT)
            .symbol(lex.TT_COMMA)
            .symbol(lex.TT_COLON)
            .literal(lex.TT_NAME, lex.NT_NAME)
            .prefix_default(lex.TT_STAR, lex.NT_VARGS)
            .prefix_default(lex.TT_DOUBLE_STAR, lex.NT_KVARGS)
    )


def ipy_parser():
    parser = (
        set_literals(builder())
            .symbol(lex.TT_RSQUARE)
            .symbol(lex.TT_COLON)
            .symbol(lex.TT_RPAREN)
            .symbol(lex.TT_RCURLY)
            # .symbol(lex.TT_COMMA)
            .symbol(lex.TT_ELSE)
            .symbol(lex.TT_ELIF)
            .symbol(lex.TT_EXCEPT)
            .symbol(lex.TT_FINALLY)
            # .symbol(lex.TT_COMMA)
            .symbol(lex.TT_END)
            .symbol(lex.TT_IN)
            .symbol(lex.TT_AS)
            .symbol(lex.TT_ENDSTREAM)

            .symbol(lex.TT_END_EXPR, prefix_empty)

            .prefix(lex.TT_INDENT, prefix_indent)
            .prefix_layout(lex.TT_LPAREN, prefix_lparen, layout_lparen)
            .prefix_layout(lex.TT_LSQUARE, prefix_lsquare, layout_lsquare)
            .prefix_layout(lex.TT_LCURLY, prefix_lcurly, layout_lcurly)
            .prefix(lex.TT_IF, prefix_if)
            .prefix(lex.TT_TRY, prefix_try)

            .prefix_default(lex.TT_NOT, lex.NT_NOT)
            .prefix_default(lex.TT_MINUS, lex.NT_NEGATE)
            .prefix_default(lex.TT_TILDE, lex.NT_BNOT)

            .stmt(lex.TT_DEF, prefix_fun)
            .prefix(lex.TT_FUN, prefix_fun)
            .prefix(lex.TT_LAMBDA, prefix_lambda)

            .infix_default(lex.TT_ASSIGN, 10, lex.NT_ASSIGN)
            .assignment(lex.TT_PLUS_ASSIGN, 10, lex.NT_PLUS_ASSIGN)
            .assignment(lex.TT_MINUS_ASSIGN, 10, lex.TT_MINUS_ASSIGN)

            .infix(lex.TT_COMMA, 10, infix_comma)
            .infix_default(lex.TT_OR, 25, lex.NT_OR)
            .infix_default(lex.TT_AND, 30, lex.NT_AND)
            .infix_default(lex.TT_LE, 35, lex.NT_LE)
            .infix_default(lex.TT_LT, 35, lex.NT_LT)
            .infix_default(lex.TT_GT, 35, lex.NT_GT)
            .infix_default(lex.TT_GE, 35, lex.NT_GE)
            .infix_default(lex.TT_EQ, 35, lex.NT_EQ)
            .infix_default(lex.TT_NE, 35, lex.NT_NE)
            .infix_default(lex.TT_IS, 35, lex.NT_IS)
            .infix_default(lex.TT_IN, 35, lex.NT_IN)
            .infix_default(lex.TT_NOT_IN, 35, lex.NT_NOT_IN)
            .infix_default(lex.TT_PIPE, 40, lex.NT_BOR)
            .infix_default(lex.TT_CARET, 40, lex.NT_BXOR)
            .infix_default(lex.TT_AMP, 45, lex.NT_BAND)
            .infix_default(lex.TT_SHL, 50, lex.NT_BSHL)
            .infix_default(lex.TT_SHR, 50, lex.NT_BSHR)

            .infix_default(lex.TT_MINUS, 55, lex.NT_SUB)
            .infix_default(lex.TT_PLUS, 55, lex.NT_ADD)
            .infix_default(lex.TT_STAR, 60, lex.NT_MUL)
            .infix_default(lex.TT_SLASH, 60, lex.NT_DIV)
            .infix_default(lex.TT_PERCENTS, 60, lex.NT_MOD)
            .infix_default(lex.TT_DOUBLE_STAR, 70, lex.NT_POW)

            .infix(lex.TT_DOT, 90, infix_dot)

            .infix(lex.TT_LSQUARE, 90, infix_lsquare)
            .infix(lex.TT_LPAREN, 90, infix_lparen)

            .stmt(lex.TT_RAISE, stmt_raise)
            .stmt(lex.TT_YIELD, stmt_yield)
            .stmt(lex.TT_RETURN, stmt_return)

            .stmt(lex.TT_WHILE, stmt_while)
            .stmt(lex.TT_FOR, stmt_for)
            .stmt(lex.TT_IMPORT, stmt_import)
            .stmt(lex.TT_FROM, stmt_from)

            .build("ipy_parser")
    )

    return (
        parser
            .add_builder("exception_name_parser", exception_name_parser())
            .add_builder("signature_parser", signature_parser())
            .add_builder("import_parser", import_parser())
            .add_builder("name_parser", name_parser())
            .add_builder("import_names_parser", import_names_parser())
    )


def parse(source):
    parser = ipy_parser()
    ts = create_stream(parser, source)
    return parse_token_stream(parser, ts)
