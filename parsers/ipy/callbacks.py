from opparse.parse import *
from opparse.indenter import (skip_indent, init_code_layout, init_free_layout,
                              init_node_layout, init_offside_layout)
from opparse import nodes, lexer
from lexicon import IpyLexicon as lex

from opparse.nodes import (
    node_0, node_1, node_2, node_3, empty_node,
    is_list_node, list_node)


# CONSTRUCTORS

def create_function_variants(args, body):
    # print "ARGS", args
    # print "BODY", body
    return list_node([list_node([args, body])])


def skip_end_expression(parser):
    parser.skip_once(parser.lex.TT_END_EXPR)


##############################################################
# INFIX
##############################################################

def infix_comma(parser, op, token, left):
    # it would be very easy, if not needed for trailing commas, aka postfix
    # operators
    tt = parser.token_type
    # check for end expr because it will be auto inserted and it has nud which
    # produces empty node
    if not parser.token_has_nud(parser.token) \
            or tt == lex.TT_END_EXPR:
        # check some corner cases with 1,2,.name or 1,2,,
        if tt == lex.TT_DOT or tt == lex.TT_COMMA:
            parse_error(parser, "Invalid tuple syntax", token)

        return left
    right = parser.expression(op.lbp)
    return node_2(lex.NT_COMMA, token, left, right)


def infix_dot(parser, op, token, left):
    parser.assert_token_type(lex.TT_NAME)
    exp = parser.expression(op.lbp)
    return node_2(lex.NT_DOT, token, left, exp)


def infix_lsquare(parser, op, token, left):
    init_free_layout(parser, token, [lex.TT_RSQUARE])
    exp = parser.expression(0)
    parser.advance_expected(lex.TT_RSQUARE)
    return node_2(lex.NT_DOT, token, left, exp)


def commas_as_list(node):
    return flatten_infix(node, lex.NT_COMMA)


def maybe_tuple(node):
    if node.node_type == lex.NT_COMMA:
        els = commas_as_list(node)
        return node_1(lex.NT_TUPLE, node.token, els)
    return node


def commas_as_list_if_commas(node):
    if node.node_type != lex.NT_COMMA:
        return node

    return flatten_infix(node, lex.NT_COMMA)


def infix_lparen(parser, op, token, left):
    if parser.token_type != lex.TT_RPAREN:
        init_free_layout(parser, token, [lex.TT_RPAREN])
        expr = parser.expression(0)
        skip_end_expression(parser)
        args = commas_as_list(expr)
    else:
        args = list_node([])
    parser.advance_expected(lex.TT_RPAREN)
    return node_2(lex.NT_CALL, token, left, args)


def infix_name_pair(parser, op, token, left):
    parser.assert_token_type(lex.TT_NAME)
    name = node_0(lex.NT_NAME, parser.token)
    parser.advance()
    return node_2(op.infix_node_type, token, left, name)


##############################################################
# INFIX
##############################################################


def prefix_indent(parser, op, token):
    return parse_error(parser, "Invalid indentation level", token)


# MOST complicated operator
# expressions (f 1 2 3) (2 + 3) (-1)
# tuples (1,2,3,4,5)
def layout_lparen(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RPAREN])


def prefix_lparen(parser, op, token):
    if parser.token_type == lex.TT_RPAREN:
        parser.advance_expected(lex.TT_RPAREN)
        return node_1(lex.NT_TUPLE, token, list_node([]))

    e = parser.terminated_expression(0, [lex.TT_RPAREN])
    skip_end_expression(parser)
    if e.node_type == lex.NT_COMMA:
        parser.advance_expected(lex.TT_RPAREN)
        items = commas_as_list(e)
        return node_1(lex.NT_TUPLE, token, items)

    parser.advance_expected(lex.TT_RPAREN)
    return e


def layout_lsquare(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RSQUARE])


def prefix_lsquare(parser, op, token):
    if parser.token_type != lex.TT_RSQUARE:
        expr = parser.expression(0)
        skip_end_expression(parser)
        args = commas_as_list(expr)
    else:
        args = list_node([])

    parser.advance_expected(lex.TT_RSQUARE)
    return node_1(lex.NT_LIST, token, args)


def layout_lcurly(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RCURLY])


def _lcurly_pair(parser):
    parser.assert_token_types([lex.TT_INT, lex.TT_STR])

    key = parser.terminated_expression(0, [lex.TT_COLON])
    parser.advance_expected(lex.TT_COLON)
    value = parser.terminated_expression(0, [lex.TT_COMMA])
    skip_end_expression(parser)
    return list_node([key, value])


def prefix_lcurly(parser, op, token):
    items = parse_struct(parser, lex.TT_RCURLY, lex.TT_COMMA, _lcurly_pair)
    return node_1(lex.NT_DICT, token, items)


def infix_if(parser, op, token, left):
    condition = parser.expression(0)
    parser.advance_expected(lex.TT_ELSE)
    else_exp = parser.expression(0)

    return node_1(lex.NT_IF, token, list_node(
        [list_node([condition, left]),
         list_node([empty_node(), else_exp])]))


def prefix_if(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_IF)
    branches = []

    cond = parser.terminated_expression(0, parser.lex.TERM_CONDITION)
    parser.advance_expected_one_of(parser.lex.TERM_CONDITION)
    init_code_layout(parser, parser.token, parser.lex.TERM_IF_BODY)

    body = parser.statements(parser.lex.TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    parser.assert_token_types(parser.lex.TERM_IF_BODY)

    while parser.token_type == lex.TT_ELIF:
        parser.advance_expected(lex.TT_ELIF)

        cond = parser.terminated_expression(0, parser.lex.TERM_CONDITION)
        parser.advance_expected_one_of(parser.lex.TERM_CONDITION)
        init_code_layout(parser, parser.token, parser.lex.TERM_IF_BODY)

        body = parser.statements(parser.lex.TERM_IF_BODY)
        parser.assert_token_types(parser.lex.TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    if parser.token_type == lex.TT_ELSE:
        parser.advance_expected(lex.TT_ELSE)
        parser.advance_expected(lex.TT_COLON)

        init_code_layout(parser, parser.token, parser.lex.TERM_BLOCK)

        body = parser.statements(parser.lex.TERM_BLOCK)
        branches.append(list_node([empty_node(), body]))
    else:
        branches.append(list_node([empty_node(), empty_node()]))

    parser.advance_end()
    return node_1(lex.NT_IF, token, list_node(branches))


def prefix_try(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_TRY)
    parser.advance_expected(lex.TT_COLON)
    init_code_layout(parser, parser.token, parser.lex.TERM_TRY)

    trybody = parser.statements(parser.lex.TERM_TRY)
    catches = []
    parser.assert_token_type(lex.TT_EXCEPT)

    while parser.token_type == lex.TT_EXCEPT:
        parser.advance_expected(lex.TT_EXCEPT)

        if parser.token_type == lex.TT_COLON:
            sig = empty_node()
        else:
            sig = parser.exception_name_parser. \
                terminated_expression(0, parser.lex.TERM_CONDITION)

        parser.advance_expected_one_of(parser.lex.TERM_CONDITION)

        init_code_layout(parser, parser.token, parser.lex.TERM_EXCEPT)
        body = parser.statements(parser.lex.TERM_EXCEPT)
        catches.append(list_node([sig, body]))

    if parser.token_type == lex.TT_FINALLY:
        parser.advance_expected(lex.TT_FINALLY)
        parser.advance_expected(lex.TT_COLON)
        init_code_layout(parser, parser.token)
        finallybody = parser.statements(parser.lex.TERM_BLOCK)
    else:
        finallybody = empty_node()

    parser.advance_end()
    return node_3(lex.NT_TRY,
                  token, trybody, list_node(catches), finallybody)


# simplify common functions

def stmt_raise(parser, op, token):
    exp = parser.expression(0)
    return node_1(lex.TT_RAISE, token, exp)


def stmt_yield(parser, op, token):
    exp = parser.expression(0)
    return node_1(lex.TT_YIELD, token, exp)


def stmt_return(parser, op, token):
    exp = parser.expression(0)
    return node_1(lex.TT_RETURN, token, exp)


# LOOPS
def check_condition(parser, condition):
    # assignment not a statement in operator precedence parser
    if condition.token_type in lex.ASSIGNMENT_TOKENS:
        parse_error(parser, "Invalid use of assignment inside condition",
                    condition.token)
    return True


def stmt_while(parser, op, token):
    init_node_layout(parser, token)
    condition = parser.terminated_expression(0, parser.lex.TERM_CONDITION)
    check_condition(parser, condition)
    parser.advance_expected(lex.TT_COLON)
    init_code_layout(parser, parser.token)
    body = parser.statements(parser.lex.TERM_BLOCK)

    return node_2(lex.NT_WHILE, token, condition, body)


def stmt_for(parser, op, token):
    init_node_layout(parser, token)

    var = parser.for_signature_parser. \
        terminated_expression(0, parser.lex.TERM_FOR_CONDITION)

    var = maybe_tuple(var)
    parser.advance_expected(lex.TT_IN)
    expr = parser.terminated_expression(0, parser.lex.TERM_CONDITION)
    parser.advance_expected(lex.TT_COLON)
    init_code_layout(parser, parser.token)
    body = parser.statements(parser.lex.TERM_BLOCK)
    parser.advance_end()
    return node_3(lex.NT_FOR, token, var, expr, body)


# CLASS
def prefix_class(parser, op, token):
    init_node_layout(parser, token)
    if parser.token_type != lex.TT_NAME:
        name = empty_node()
    else:
        name = grab_name(parser.name_parser)

    if parser.token_type == lex.TT_LPAREN:
        parser.advance()
        init_free_layout(parser, token, [lex.TT_RPAREN])
        expr = parser.expression(0)
        skip_end_expression(parser)
        parents = commas_as_list(expr)
        parser.advance_expected(lex.TT_RPAREN)
    else:
        parents = empty_node()

    parser.advance_expected(lex.TT_COLON)
    init_code_layout(parser, parser.token)
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
    init_free_layout(parser, token, [lex.TT_RPAREN])
    if parser.token_type != lex.TT_RPAREN:
        expr = parser.signature_parser.expression(0)
        skip_end_expression(parser)
        args = commas_as_list(expr)
    else:
        args = list_node([])
    parser.advance_expected(lex.TT_RPAREN)
    parser.advance_expected(lex.TT_COLON)
    init_code_layout(parser, parser.token)
    body = parser.statements(parser.lex.TERM_BLOCK)
    return args, body


# TODO TRY DO IT IN COMPLETELY OPERATOR WAY
def prefix_fun(parser, op, token):
    init_node_layout(parser, token)
    if parser.token_type == lex.TT_LPAREN:
        name = empty_node()
    else:
        name = grab_name(parser.name_parser)
    args, body = _parse_function(parser, token)
    parser.advance_end()
    return node_3(lex.NT_FUN, token, name, args, body)


def stmt_def(parser, op, token):
    init_node_layout(parser, token)
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
