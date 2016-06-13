from opparse.parse import *
from opparse import nodes, lexer
from lexicon import LuaLexicon as lex

from opparse.nodes import (
    node_0, node_1, node_2, node_3, empty_node,
    is_list_node, list_node)


def commas_as_list(node):
    return flatten_infix(node, lex.NT_COMMA)

##############################################################
# INFIX
##############################################################


def infix_name_to_the_right(parser, op, token, left):
    parser.assert_node_type(left, lex.NT_NAME)
    parser.assert_token_type(lex.TT_NAME)
    exp = parser.expression(op.lbp)
    return node_2(op.infix_node_type, token, left, exp)


# TODO parser common
def infix_assign(parser, op, token, left):
    if left.node_type == lex.NT_COMMA:
        names = commas_as_list(left)
    else:
        parser.assert_node_types(left,
                                 [lex.NT_NAME, lex.NT_DOT, lex.NT_LOOKUP])
        names = nodes.ensure_list(left)

    vals = [parser.expression_parser.expression(0)]
    while parser.token_type == lex.TT_COMMA:
        parser.advance_expected(lex.TT_COMMA)
        vals.append(parser.expression_parser.expression(0))

    return node_2(lex.NT_ASSIGN, token, names, list_node(vals))


def infix_statement_lsquare(parser, op, token, left):
    return infix_lsquare(parser.expression_parser, op, token, left)


def infix_lsquare(parser, op, token, left):
    exp = parser.expression(0)
    parser.advance_expected(lex.TT_RSQUARE)
    return node_2(lex.NT_LOOKUP, token, left, exp)


def infix_statement_lparen(parser, op, token, left):
    return infix_lparen(parser.expression_parser, op, token, left)


def infix_lparen(parser, op, token, left):
    args = parse_struct(parser, lex.TT_RPAREN, lex.TT_COMMA)
    return node_2(lex.NT_CALL, token, left, args)


def infix_name_pair(parser, op, token, left):
    parser.assert_token_type(lex.TT_NAME)
    name = node_0(lex.NT_NAME, parser.token)
    parser.advance()
    return node_2(op.infix_node_type, token, left, name)


def prefix_lparen(parser, op, token):
    return parser.maybe_expression(0, lex.TT_RPAREN, empty_node())


# TABLES

def _table_item(parser):
    if parser.token_type == lex.TT_LSQUARE:
        parser.advance()
        key = parser.expression(0)
        parser.advance_expected(lex.TT_RSQUARE)
        parser.advance_expected(lex.TT_ASSIGN)
        value = parser.expression(0)
    else:
        key = parser.expression(0)
        if parser.token_type == lex.TT_ASSIGN:
            parser.assert_node_type(key, lex.NT_NAME)
            parser.advance_expected(lex.TT_ASSIGN)
            value = parser.expression(0)
        else:
            value = key
            key = empty_node()

    return list_node([key, value])


def prefix_lcurly(parser, op, token):
    items = parse_struct(parser, lex.TT_RCURLY, lex.TT_COMMA, _table_item)

    return node_1(lex.NT_TABLE, token, items)


def stmt_if(parser, op, token):
    branches = []
    exp_parser = parser.expression_parser
    cond = exp_parser.expression(0)
    parser.advance_expected(lex.TT_THEN)

    body = parser.statements(parser.lex.TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    parser.assert_token_types(parser.lex.TERM_IF_BODY)

    while parser.token_type == lex.TT_ELSEIF:
        parser.advance_expected(lex.TT_ELSEIF)

        cond = exp_parser.expression(0)
        parser.advance_expected(lex.TT_THEN)
        body = parser.statements(parser.lex.TERM_IF_BODY)
        parser.assert_token_types(parser.lex.TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    if parser.token_type == lex.TT_ELSE:
        parser.advance_expected(lex.TT_ELSE)
        else_body = parser.statements(parser.lex.TERM_BLOCK)
    else:
        else_body = empty_node()

    branches.append(list_node([empty_node(), else_body]))
    parser.advance_end()
    return node_1(lex.NT_IF, token, list_node(branches))


def stmt_local(parser, op, token):
    s = parser.statement()
    parser.assert_node_types(s, [lex.NT_ASSIGN, lex.NT_NAME, lex.NT_COMMA])
    if s.node_type == lex.NT_COMMA:
        s = commas_as_list(s)

    return node_1(lex.NT_LOCAL, token, s)


def stmt_return(parser, op, token):
    items = [parser.expression_parser.expression(0)]
    while parser.token_type == lex.TT_COMMA:
        parser.advance_expected(lex.TT_COMMA)
        items.append(parser.expression_parser.expression(0))

    return node_1(lex.TT_RETURN, token, list_node(items))


def stmt_while(parser, op, token):
    condition = parser.expression_parser.expression(0)
    parser.advance_expected(lex.TT_DO)
    body = parser.statements(parser.lex.TERM_BLOCK)
    parser.advance_end()
    return node_2(lex.NT_WHILE, token, condition, body)


def stmt_repeat(parser, op, token):
    body = parser.statements(parser.lex.TERM_REPEAT)
    parser.advance_expected(lex.TT_UNTIL)
    condition = parser.expression_parser.expression(0)
    return node_2(lex.NT_REPEAT, token, condition, body)


def stmt_for(parser, op, token):
    var_name = grab_name(parser)
    # numeric for
    """
    numeric for can have 2 or 3 expressions for name=exp1,exp2 (,exp3)? do
    """
    if parser.token_type == lex.TT_ASSIGN:
        exps = []
        parser.advance()
        exp1 = parser.expression_parser.expression(0)
        exps.append(exp1)
        if parser.token_type == lex.TT_COMMA:
            parser.advance_expected(lex.TT_COMMA)
            exp2 = parser.expression_parser.expression(0)
            exps.append(exp2)
            if parser.token_type == lex.TT_COMMA:
                parser.advance_expected(lex.TT_COMMA)
                exp3 = parser.expression_parser.expression(0)
                exps.append(exp3)

        parser.advance_expected(lex.TT_DO)
        body = parser.statements(lex.TERM_BLOCK)
        parser.advance_end()
        return node_3(lex.NT_NUMERIC_FOR, token,
                      var_name, list_node(exps), body)
    else:
        names = [var_name]
        while parser.token_type != lex.TT_IN:
            parser.advance_expected(lex.TT_COMMA)
            name = grab_name(parser)
            names.append(name)

        parser.advance_expected(lex.TT_IN)
        expr = parser.expression_parser.expression(0)
        parser.advance_expected(lex.TT_DO)
        body = parser.statements(lex.TERM_BLOCK)
        parser.advance_end()
        return node_3(lex.NT_GENERIC_FOR, token, list_node(names), expr, body)

# FUNCTION STUFF################################


def grab_name(parser):
    parser.assert_token_type(lex.TT_NAME)
    name = node_0(lex.NT_NAME, parser.token)
    parser.advance()
    return name


def _parse_function(parser, token):
    parser.advance_expected(lex.TT_LPAREN)
    args = parse_struct(parser.signature_parser, lex.TT_RPAREN, lex.TT_COMMA)
    body = parser.statements(parser.lex.TERM_BLOCK)
    parser.advance_end()
    return args, body


# TODO TRY DO IT IN COMPLETELY OPERATOR WAY
def prefix_function(parser, op, token):
    args, body = _parse_function(parser.statement_parser, token)
    return node_2(lex.NT_LAMBDA, token, args, body)


def stmt_function(parser, op, token):
    parser.assert_token_type(lex.TT_NAME)
    name = grab_name(parser)
    args, body = _parse_function(parser, token)
    return node_3(lex.NT_FUNCTION, token, name, args, body)
