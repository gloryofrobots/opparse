from opparse.parse import *
from opparse import nodes, lexer
from lexicon import IpyLexicon as lex

from opparse.nodes import (
    node_0, node_1, node_2, node_3, empty_node,
    is_list_node, list_node)

##############################################################
# INFIX
##############################################################


def infix_name_to_the_right(parser, op, token, left):
    parser.assert_node_type(left, lex.NT_NAME)
    parser.assert_token_type(lex.TT_NAME)
    exp = parser.expression(op.lbp)
    return node_2(op.infix_node_type, token, left, exp)


def infix_lsquare(parser, op, token, left):
    exp = parser.expression(0)
    parser.advance_expected(lex.TT_RSQUARE)
    return node_2(lex.NT_DOT, token, left, exp)


def commas_as_list(node):
    return flatten_infix(node, lex.NT_COMMA)


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

def prefix_table_lsquare(parser, op, token):
    exp = parser.expression_parser.expression(0)
    parser.advance_expected(lex.TT_RSQUARE)
    return exp


def _table_item(parser):
    key = parser.expression(0)
    parser.advance_expected(lex.TT_ASSIGN)
    value = parser.expression_parser.expression(0)
    return list_node([key, value])


def prefix_lcurly(parser, op, token):
    items = parse_struct(parser.table_parser,
                         _table_item, lex.TT_RCURLY, lex.TT_COMMA)

    return node_1(lex.NT_TABLE, token, items)


def prefix_if(parser, op, token):
    branches = []
    cond = parser.expression(0)
    parser.advance_expected(lex.TT_THEN)

    body = parser.statements(parser.lex.TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    parser.assert_token_types(parser.lex.TERM_IF_BODY)

    while parser.token_type == lex.TT_ELSEIF:
        parser.advance_expected(lex.TT_ELSEIF)

        cond = parser.expression(0)
        parser.advance_expected(lex.TT_THEN)
        body = parser.statements(parser.lex.TERM_IF_BODY)
        parser.assert_token_types(parser.lex.TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    if parser.token_type == lex.TT_ELSE:
        parser.advance_expected(lex.TT_ELSE)
        parser.advance_expected(lex.TT_COLON)

        else_body = parser.statements(parser.lex.TERM_BLOCK)
    else:
        else_body = empty_body()

    branches.append(list_node([empty_node(), else_body]))
    parser.advance_end()
    return node_1(lex.NT_IF, token, list_node(branches))


def stmt_return(parser, op, token):
    items = [parser.expression_parser.expression(0)]
    while parser.token_type == lex.TT_COMMA:
        parser.advance_expected(lex.TT_COMMA)
        items.append(parser.expression_parser.expression(0))

    return node_1(lex.TT_RETURN, token, list_node(items))


def stmt_while(parser, op, token):
    condition = parser.expressions_parser. \
        terminated_expression(0, parser.lex.LOOP_CONDITION)

    parser.advance_expected(lex.TT_DO)
    body = parser.statements(parser.lex.TERM_BLOCK)
    return node_2(lex.NT_WHILE, token, condition, body)

def stmt_repeat(parser, op, token):
    body = parser.statements(parser.lex.TERM_UNTIL)
    parser.advance_expected(lex.TT_UNTIL)
    condition = parser.expressions_parser.expression(0)
    return node_2(lex.NT_REPEAT, token, condition, body)


def stmt_for(parser, op, token):
    var = parser.for_signature_parser. \
        terminated_expression(0, parser.lex.TERM_FOR_CONDITION)

    var = maybe_tuple(var)
    parser.advance_expected(lex.TT_IN)
    expr = parser.terminated_expression(0, parser.lex.TERM_CONDITION)
    parser.advance_expected(lex.TT_COLON)
    body = parser.statements(parser.lex.TERM_BLOCK)
    parser.advance_end()
    return node_3(lex.NT_FOR, token, var, expr, body)


# CLASS
def prefix_class(parser, op, token):
    if parser.token_type != lex.TT_NAME:
        name = empty_node()
    else:
        name = grab_name(parser.name_parser)

    if parser.token_type == lex.TT_LPAREN:
        parser.advance()
        expr = parser.expression(0)
        skip_end_expression(parser)
        parents = commas_as_list(expr)
        parser.advance_expected(lex.TT_RPAREN)
    else:
        parents = empty_node()

    parser.advance_expected(lex.TT_COLON)
    body = parser.statements(lex.TERM_BLOCK)
    parser.advance_end()
    return node_3(lex.NT_CLASS, token, name, parents, body)


# FUNCTION STUFF################################
def grab_name(parser):
    parser.assert_token_type(lex.TT_NAME)
    name = node_0(lex.NT_NAME, parser.token)
    parser.advance()
    return name


def _parse_function(parser, token):
    parser.advance_expected(lex.TT_LPAREN)
    if parser.token_type != lex.TT_RPAREN:
        expr = parser.signature_parser.expression(0)
        skip_end_expression(parser)
        args = commas_as_list(expr)
    else:
        args = list_node([])
    parser.advance_expected(lex.TT_RPAREN)
    parser.advance_expected(lex.TT_COLON)
    body = parser.statements(parser.lex.TERM_BLOCK)
    return args, body


# TODO TRY DO IT IN COMPLETELY OPERATOR WAY
def prefix_fun(parser, op, token):
    if parser.token_type == lex.TT_LPAREN:
        name = empty_node()
    else:
        name = grab_name(parser.name_parser)
    args, body = _parse_function(parser, token)
    parser.advance_end()
    return node_3(lex.NT_FUN, token, name, args, body)


def stmt_def(parser, op, token):
    parser.assert_token_type(lex.TT_NAME)
    name = grab_name(parser.name_parser)
    args, body = _parse_function(parser, token)
    parser.advance_end()
    return node_3(lex.NT_FUN, token, name, args, body)


def prefix_lambda(parser, op, token):
    args = []
    while parser.token_type != lex.TT_COLON:
        args.append(parser.signature_parser.expression(0))
        if parser.token_type != lex.TT_COMMA:
            break

        parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_COLON)

    body = parser.expression(0)
    return node_3(lex.NT_FUN, token, empty_node(), list_node(args), body)


###############################################################
# IMPORT STATEMENTS
###############################################################
# import callbacks are not error prone
# you need better tuned parsers to do it properly
# for example, current implementation allows
# import mod1.mod2.file as mod3.file
def stmt_from(parser, op, token):
    module = parser.import_parser.expression(0)
    parser.advance_expected(lex.TT_IMPORT)
    what = parser.import_parser.expression(0)
    return node_2(lex.NT_IMPORT_FROM, token, module, what)


def stmt_import(parser, op, token):
    imported = parser.import_parser.expression(0)
    return node_1(lex.NT_IMPORT, token, imported)
