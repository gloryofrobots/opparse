import lexicon
from opparse import tokenstream
# TODO RENAME
from callbacks import *

lex = lexicon.LuaLexicon()


class LuaParser(Parser):

    def advance_end(self):
        self.advance_expected(self.lex.TT_END)

    # def endofexpression(self):
    #     if self.isend():
    #         return False
    #     if self.token_type in self.lex.TERM_BLOCK:
    #         return True
    #     if self.token_type == self.lex.TT_END_EXPR:
    #         self.advance()
    #         return True
    #     return False


def builder(**settings):
    return LuaParser.builder(lex, settings)


def set_literals(parser_builder):
    return (
        parser_builder
        .literal(lex.TT_INT, lex.NT_INT)
        .literal(lex.TT_STR, lex.NT_STR)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .literal(lex.TT_TRUE, lex.NT_TRUE)
        .literal(lex.TT_FALSE, lex.NT_FALSE)
        .literal(lex.TT_NIL, lex.NT_NIL)
    )


def signature_parser():
    return (
        builder()
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_LPAREN)
        .symbol(lex.TT_COMMA)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .prefix(lex.TT_DOT_3, prefix_dot_3)
    )


def table_parser(expressions_parser):
    parser = (
        builder(break_on_juxtaposition=True)
        .symbol(lex.TT_ASSIGN)
        .symbol(lex.TT_COMMA)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .literal(lex.TT_INT, lex.NT_INT)
        # .prefix(lex.TT_LSQUARE, prefix_table_lsquare)
    ).build("table_parser")

    return parser.add_weakref(expressions_parser)


def expression_parser(statement_parser):
    parser = (
        set_literals(builder(break_on_juxtaposition=True))
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ASSIGN)
        .symbol(lex.TT_RPAREN)
        .symbol(lex.TT_RCURLY)
        .symbol(lex.TT_COMMA)
        .symbol(lex.TT_IN)
        .symbol(lex.TT_IF)
        .symbol(lex.TT_ELSEIF)
        .symbol(lex.TT_ELSE)
        .symbol(lex.TT_THEN)
        .symbol(lex.TT_LOCAL)
        .symbol(lex.TT_RETURN)
        .symbol(lex.TT_WHILE)
        .symbol(lex.TT_REPEAT)
        .symbol(lex.TT_UNTIL)
        .symbol(lex.TT_DO)
        .symbol(lex.TT_FOR)
        .symbol(lex.TT_BREAK)
        .symbol(lex.TT_END_EXPR, prefix_empty)
        .symbol(lex.TT_ENDSTREAM)
        .symbol(lex.TT_END)

        .prefix(lex.TT_LPAREN, prefix_lparen)
        .prefix(lex.TT_LCURLY, prefix_lcurly)

        .prefix_default(lex.TT_NOT, lex.NT_NOT)
        .prefix_default(lex.TT_MINUS, lex.NT_NEGATE)

        .prefix(lex.TT_FUNCTION, prefix_function)

        .infix_default(lex.TT_OR, 20, lex.NT_OR)
        .infix_default(lex.TT_AND, 30, lex.NT_AND)
        .infix_default(lex.TT_LE, 35, lex.NT_LE)
        .infix_default(lex.TT_LT, 35, lex.NT_LT)
        .infix_default(lex.TT_GT, 35, lex.NT_GT)
        .infix_default(lex.TT_GE, 35, lex.NT_GE)
        .infix_default(lex.TT_EQ, 35, lex.NT_EQ)
        .infix_default(lex.TT_NE, 35, lex.NT_NE)

        .infix_default(lex.TT_DOT_2, 40, lex.NT_CONCAT)

        .infix_default(lex.TT_MINUS, 50, lex.NT_SUB)
        .infix_default(lex.TT_PLUS, 50, lex.NT_ADD)
        .infix_default(lex.TT_STAR, 60, lex.NT_MUL)
        .infix_default(lex.TT_SLASH, 60, lex.NT_DIV)
        .infix_default(lex.TT_PERCENTS, 60, lex.NT_MOD)
        .infix_default(lex.TT_CARET, 60, lex.NT_POW)

        .infix(lex.TT_DOT, 90, infix_name_to_the_right, lex.NT_DOT)
        .infix(lex.TT_COLON, 90, infix_name_to_the_right, lex.NT_COLON)
        .infix(lex.TT_LSQUARE, 90, infix_lsquare)
        .infix(lex.TT_LPAREN, 90, infix_lparen)

    ).build("expression_parser")

    return (
        parser
        .add_weakref(statement_parser)
        .add_subparser(table_parser(parser))
    )


def lua_parser():
    parser = (
        builder(break_on_juxtaposition=True)
        .literal(lex.TT_NAME, lex.NT_NAME)
        .symbol(lex.TT_IN)
        .symbol(lex.TT_RSQUARE)
        .symbol(lex.TT_ELSEIF)
        .symbol(lex.TT_ELSE)
        .symbol(lex.TT_THEN)
        .symbol(lex.TT_UNTIL)
        .symbol(lex.TT_END_EXPR, prefix_empty)
        .symbol(lex.TT_END)
        .symbol(lex.TT_ENDSTREAM)

        .stmt(lex.TT_FUNCTION, stmt_function)

        # .infix(lex.TT_COMMA, 10, infix_comma)
        .infix_default(lex.TT_COMMA, 10, lex.NT_COMMA)
        .infix(lex.TT_ASSIGN, 5, infix_assign)

        .infix(lex.TT_DOT, 90, infix_name_to_the_right, lex.NT_DOT)
        .infix(lex.TT_COLON, 90, infix_name_to_the_right, lex.NT_COLON)
        .infix(lex.TT_LSQUARE, 90, infix_statement_lsquare)
        .infix(lex.TT_LPAREN, 90, infix_statement_lparen)  # 
        # TODO add infix lcurly
        #.infix(lex.TT_LCURLY, 90, infix_lcurly)

        .literal(lex.TT_BREAK, lex.NT_BREAK)

        .stmt(lex.TT_LOCAL, stmt_local)
        .stmt(lex.TT_RETURN, stmt_return)
        .stmt(lex.TT_IF, stmt_if)
        .stmt(lex.TT_REPEAT, stmt_repeat)
        .stmt(lex.TT_WHILE, stmt_while)
        .stmt(lex.TT_FOR, stmt_for)
    ).build("lua_parser")

    return (
        parser
        # expression and statement parsers must have cycle refs to each other
        .add_subparser(expression_parser(parser))
        .add_builder("signature_parser", signature_parser())
    )


def parse(source):
    parser = lua_parser()
    lx = lexer.Lexer(parser.lex, source)
    ts = tokenstream.TokenStream(lx.as_generator(), source)
    return parse_token_stream(parser, ts)
