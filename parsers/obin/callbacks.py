from opparse.parse import *
from opparse.indenter import (skip_indent, init_code_layout, init_free_layout,
                              init_node_layout, init_offside_layout)

from opparse import nodes, lexer
from opparse.misc import strutil
from lexicon import ObinLexicon as lex

from opparse.nodes import (
    node_0, node_1, node_2, node_3, empty_node,
    is_list_node, list_node)


# CONSTRUCTORS

def create_function_variants(args, body):
    # print "ARGS", args
    # print "BODY", body
    return list_node([list_node([args, body])])



def create_name_node_s(token, name):
    return node_0(lex.NT_NAME, token)


def create_name_from_operator(token, op):
    return create_name_node_s(token, op.token_value)


def create_symbol_node(token, name):
    return node_1(lex.NT_SYMBOL, token, name)


def create_symbol_node_s(token, name):
    return node_1(lex.NT_SYMBOL, token, create_name_node_s(token, name))


def create_tuple_node(token, elements):
    return node_1(lex.NT_TUPLE,
                  token,
                  list_node(elements))


def create_tuple_node_from_list(token, elements):
    assert is_list_node(elements)
    return node_1(lex.NT_TUPLE, token, elements)


def create_list_node(token, items):
    return node_1(lex.NT_LIST, token, list_node(items))


def create_list_node_from_list(token, items):
    assert is_list_node(items)
    return node_1(lex.NT_LIST, token , items)


def create_empty_list_node(token):
    return node_1(lex.NT_LIST, token, list_node([]))


def create_call_node_2(token, func, exp1, exp2):
    return node_2(lex.NT_CALL, token, func, list_node([exp1, exp2]))


def create_call_node(token, funcname, exps):
    return node_2(lex.NT_CALL,
                  token,
                  create_name_node_s(token, funcname),
                  list_node(exps))


# JUXTAPOSITION

def juxtaposition_as_list(parser, terminators):
    token = parser.token
    exp = parser.terminated_expression(0, terminators)
    if not nodes.is_list_node(exp):
        return create_list_node(token, [exp])

    return create_list_node_from_list(token, exp)


def juxtaposition_as_tuple(parser, terminators):
    token = parser.token
    exp = parser.terminated_expression(0, terminators)
    if not nodes.is_list_node(exp):
        return create_tuple_node(token, [exp])

    return create_tuple_node_from_list(token, exp)




#####################


def is_wildcard_node(n):
    return n.node_type == lex.NT_WILDCARD


def tuple_node_length(n):
    assert n.node_type == lex.NT_TUPLE
    return len(n.first())


def _init_default_current_0(parser):
    return nodes.node_0(parser.lex.token_node_type(parser.token),
                        parser.token)


# additional helpers


def skip_end_expression(parser):
    parser.skip_once(parser.lex.TT_END_EXPR)


def expression_with_optional_end_of_expression(parser, _rbp, terminators):
    exp = parser.terminated_expression(_rbp, terminators)
    skip_end_expression(parser)
    return exp


def prefix_nud_function(parser, op, token):
    exp = parser.literal_expression()
    # exp = expression(parser, 100)
    return create_call_node(token, op.prefix_function, [exp])


def infix_led_function(parser, op, token, left):
    exp = parser.expression(op.lbp)
    return create_call_node(token, op.infix_function, [left, exp])


def infixr_led_function(parser, op, token, left):
    exp = parser.rexpression(op)
    return create_call_node(token, op.infix_function, [left, exp])


##############################################################
# INFIX
##############################################################

def infix_backtick_name(parser, op, token, left):
    funcname = strutil.cat_both_ends(token.value)
    if not funcname:
        return parse_error(parser,
                           "invalid variable name in backtick expression",
                           token)
    funcnode = create_name_node_s(token, funcname)

    right = parser.expression(op.lbp)
    return create_call_node_2(token, funcnode, left, right)



def infix_juxtaposition(parser, op, token, left):
    right = parser.base_expression(op.lbp, None)
    return nodes.node_2(lex.NT_JUXTAPOSITION, token, left, right)


def infix_dot(parser, op, token, left):
    if parser.token_type == lex.TT_INT:
        idx = _init_default_current_0(parser)
        parser.advance()
        return node_2(lex.NT_LOOKUP, token, left, idx)

    symbol = grab_name(parser)
    return node_2(lex.NT_LOOKUP,
                  token, left, create_symbol_node(token, symbol))


def infix_lcurly(parser, op, token, left):
    items = []
    init_free_layout(parser, token, [lex.TT_RCURLY])
    if parser.token_type != lex.TT_RCURLY:
        while True:
            # TODO check it
            parser.assert_token_types(
                [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT,
                 lex.TT_STR, lex.TT_MULTI_STR, lex.TT_CHAR, lex.TT_FLOAT])

            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = parser.expression(10)

            parser.advance_expected(lex.TT_ASSIGN)
            value = parser.expression(0)

            items.append(list_node([key, value]))

            if parser.token_type != lex.TT_COMMA:
                break

            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RCURLY)
    return node_2(lex.NT_MODIFY, token, left, list_node(items))


def infix_lsquare(parser, op, token, left):
    init_free_layout(parser, token, [lex.TT_RSQUARE])
    exp = parser.expression(0)
    parser.advance_expected(lex.TT_RSQUARE)
    return node_2(lex.NT_LOOKUP, token, left, exp)


def infix_lparen(parser, op, token, left):
    init_free_layout(parser, token, [lex.TT_RPAREN])

    items = []
    if parser.token_type != lex.TT_RPAREN:
        while True:
            items.append(parser.expression(0))
            skip_end_expression(parser)

            if parser.token_type != lex.TT_COMMA:
                break

            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RPAREN)
    return node_2(lex.NT_CALL, token, left, list_node(items))


def infix_name_pair(parser, op, token, left):
    parser.assert_token_type(lex.TT_NAME)
    name = _init_default_current_0(parser)
    parser.advance()
    return node_2(parser.lex.token_node_type(token), token, left, name)


def infix_at(parser, op, token, left):
    ltype = left.token_type
    if ltype != lex.TT_NAME:
        parse_error(parser, "Bad lvalue in pattern binding", left)

    exp = parser.expression(9)
    return node_2(lex.NT_BIND, token, left, exp)


##############################################################
# INFIX
##############################################################


def prefix_indent(parser, op, token):
    return parse_error(parser, "Invalid indentation level", token)


def _parse_name(parser):
    if parser.token_type == lex.TT_SHARP:
        token = parser.token
        parser.advance()
        return _parse_symbol(parser, token)

    parser.assert_token_types([lex.TT_STR, lex.TT_MULTI_STR, lex.TT_NAME])
    token = parser.token
    parser.advance()
    return node_0(parser.lex.token_node_type(token), token)


def _parse_symbol(parser, token):
    parser.assert_token_types(
        [lex.TT_NAME, lex.TT_MULTI_STR, lex.TT_STR, lex.TT_OPERATOR])
    exp = node_0(parser.lex.token_node_type(parser.token), parser.token)
    parser.advance()
    return node_1(parser.lex.token_node_type(token), token, exp)


def prefix_backtick_operator(parser, op, token):
    opname = strutil.cat_both_ends(token.value)
    if opname == "::":
        return create_name_node_s(token, "cons")

    op = parser.find_custom_operator(opname)
    if op is None:
        return parse_error(parser, "Invalid operator", token)
    if op.infix_function is None:
        return parse_error(parser, "Expected infix operator", token)

    return create_name_node_s(token, op.infix_function)


def prefix_sharp(parser, op, token):
    return _parse_symbol(parser, token)


def symbol_wildcard(parser, op, token):
    return parse_error(parser, "Invalid use of _ pattern", token)


# MOST complicated operator
# expressions (f 1 2 3) (2 + 3) (-1)
# tuples (1,2,3,4,5)
def layout_lparen(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RPAREN])


def prefix_lparen(parser, op, token):
    if parser.token_type == lex.TT_RPAREN:
        parser.advance_expected(lex.TT_RPAREN)
        return node_0(lex.NT_UNIT, token)

    e = parser.terminated_expression(0, [lex.TT_RPAREN])
    skip_end_expression(parser)

    if parser.token_type == lex.TT_RPAREN:
        parser.advance_expected(lex.TT_RPAREN)
        return e

    items = [e]
    parser.advance_expected(lex.TT_COMMA)

    if parser.token_type != lex.TT_RPAREN:
        while True:
            items.append(parser.terminated_expression(0, [lex.TT_COMMA]))
            skip_end_expression(parser)
            if parser.token_type == lex.TT_RPAREN:
                break
            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RPAREN)
    return node_1(lex.NT_TUPLE, token, list_node(items))


def layout_lsquare(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RSQUARE])


def prefix_lsquare(parser, op, token):
    items = []
    if parser.token_type != lex.TT_RSQUARE:
        while True:
            items.append(parser.expression(0))
            skip_end_expression(parser)

            if parser.token_type != lex.TT_COMMA:
                break

            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RSQUARE)
    return node_1(lex.NT_LIST, token, list_node(items))


def on_bind_node(parser, key):
    if key.node_type != lex.NT_NAME:
        parse_error(parser, "Invalid bind name", key)
    if parser.token_type == lex.TT_OF:
        parser.advance_expected(lex.TT_OF)
        parser.assert_token_type(lex.TT_NAME)
        typename = grab_name(parser)
        return node_2(lex.NT_OF,
                      key.token,
                      key, typename), empty_node()

    parser.advance_expected(lex.TT_AT_SIGN)
    real_key, value = _parse_map_key_pair(
        parser, [lex.TT_NAME,
                 lex.TT_SHARP, lex.TT_STR,
                 lex.TT_MULTI_STR], None)

    # allow syntax like {var1@ key}
    if real_key.node_type == lex.NT_NAME:
        real_key = create_symbol_node(real_key.token, real_key)

    bind_key = node_2(lex.NT_BIND, key.token, key, real_key)

    return bind_key, value


def prefix_lcurly_type(parser, op, token):
    items = []
    if parser.token_type != lex.TT_RCURLY:
        while True:
            name = parser.expression(0)
            skip_end_expression(parser)
            parser.assert_node_type(name, lex.NT_SYMBOL)

            items.append(name)
            if parser.token_type != lex.TT_COMMA:
                break

            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RCURLY)
    return node_1(lex.NT_LIST, token, list_node(items))


def layout_lcurly(parser, op, token):
    init_free_layout(parser, token, [lex.TT_RCURLY])


# this callback used in pattern matching
def prefix_lcurly_patterns(parser, op, token):
    return _prefix_lcurly(parser, op, token,
                          [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT,
                           lex.TT_MULTI_STR, lex.TT_STR,
                           lex.TT_CHAR, lex.TT_FLOAT],
                          on_bind_node)


def prefix_lcurly(parser, op, token):
    return _prefix_lcurly(parser, op, token,
                          [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT,
                           lex.TT_STR, lex.TT_MULTI_STR,
                           lex.TT_CHAR, lex.TT_FLOAT],
                          on_bind_node)


def _parse_map_key_pair(parser, types, on_unknown):
    parser.assert_token_types(types)
    # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
    key = parser.expression(10)

    if parser.token_type == lex.TT_COMMA:
        value = empty_node()
    elif parser.token_type == lex.TT_RCURLY:
        value = empty_node()
    elif parser.token_type == lex.TT_ASSIGN:
        parser.advance_expected(lex.TT_ASSIGN)
        value = parser.expression(0)
        skip_end_expression(parser)
    else:
        if on_unknown is None:
            parse_error(parser, "Invalid map declaration syntax", parser.token)
        key, value = on_unknown(parser, key)

    return key, value


def _prefix_lcurly(parser, op, token, types, on_unknown):
    # on_unknown used for pattern_match in binds {NAME @ name = "Alice"}
    items = []
    if parser.token_type != lex.TT_RCURLY:
        while True:
            # TODO check it
            key, value = _parse_map_key_pair(parser, types, on_unknown)
            items.append(list_node([key, value]))

            if parser.token_type != lex.TT_COMMA:
                break

            parser.advance_expected(lex.TT_COMMA)

    parser.advance_expected(lex.TT_RCURLY)
    return node_1(lex.NT_MAP, token, list_node(items))


def prefix_if(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_IF)
    branches = []

    cond = parser.terminated_expression(0, parser.lex.TERM_IF_CONDITION)
    parser.advance_expected_one_of(parser.lex.TERM_IF_CONDITION)
    init_code_layout(parser, parser.token, parser.lex.TERM_IF_BODY)

    body = parser.statements(parser.lex.TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    parser.assert_token_types(parser.lex.TERM_IF_BODY)

    while parser.token_type == lex.TT_ELIF:
        parser.advance_expected(lex.TT_ELIF)

        cond = parser.terminated_expression(0, parser.lex.TERM_IF_CONDITION)
        parser.advance_expected_one_of(parser.lex.TERM_IF_CONDITION)
        init_code_layout(parser, parser.token, parser.lex.TERM_IF_BODY)

        body = parser.statements(parser.lex.TERM_IF_BODY)
        parser.assert_token_types(parser.lex.TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    parser.advance_expected(lex.TT_ELSE)
    init_code_layout(parser, parser.token, parser.lex.TERM_BLOCK)

    body = parser.statements(parser.lex.TERM_BLOCK)
    branches.append(list_node([empty_node(), body]))
    parser.advance_end()
    return node_1(lex.NT_CONDITION, token, list_node(branches))


def prefix_let(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_LET)
    init_code_layout(parser, parser.token, parser.lex.TERM_LET)
    letblock = parser.statements(parser.lex.TERM_LET)
    parser.advance_expected(lex.TT_IN)
    skip_indent(parser)
    init_code_layout(parser, parser.token)
    inblock = parser.statements(parser.lex.TERM_BLOCK)
    parser.advance_end()
    return node_2(lex.NT_LET, token, letblock, inblock)


def prefix_try(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_TRY)
    init_code_layout(parser, parser.token, parser.lex.TERM_TRY)

    trybody = parser.statements(parser.lex.TERM_TRY)
    catches = []

    parser.assert_token_type(lex.TT_CATCH)
    parser.advance()
    skip_indent(parser)

    if parser.token_type == lex.TT_CASE:
        init_offside_layout(parser, parser.token)
        while parser.token_type == lex.TT_CASE:
            parser.advance_expected(lex.TT_CASE)
            # pattern = expressions(parser.pattern_parser, 0)
            pattern = _parse_pattern(parser)
            parser.advance_expected(lex.TT_ARROW)
            init_code_layout(parser, parser.token, parser.lex.TERM_CATCH_CASE)
            body = parser.statements(parser.lex.TERM_CATCH_CASE)
            catches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        parser.advance_expected(lex.TT_ARROW)
        init_code_layout(parser, parser.token, parser.lex.TERM_SINGLE_CATCH)
        body = parser.statements(parser.lex.TERM_SINGLE_CATCH)
        catches.append(list_node([pattern, body]))

    if parser.token_type == lex.TT_FINALLY:
        parser.advance_expected(lex.TT_FINALLY)
        parser.advance_expected(lex.TT_ARROW)
        init_code_layout(parser, parser.token)
        finallybody = parser.statements(parser.lex.TERM_BLOCK)
    else:
        finallybody = empty_node()

    parser.advance_end()

    return node_3(lex.NT_TRY,
                  token, trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = parser.pattern_parser.terminated_expression(0, parser.lex.TERM_PATTERN)
    if parser.token_type == lex.TT_WHEN:
        parser.advance()
        guard = parser.guard_parser.terminated_expression(0, parser.lex.TERM_FUN_GUARD)
        pattern = node_2(lex.NT_WHEN, guard.token, pattern, guard)

    return pattern


def prefix_match(parser, op, token):
    init_node_layout(parser, token, parser.lex.LEVELS_MATCH)
    init_code_layout(parser, parser.token, parser.lex.TERM_MATCH_EXPR)

    exp = expression_with_optional_end_of_expression(
        parser, 0, parser.lex.TERM_MATCH_PATTERN)
    # skip_indent(parser)
    parser.assert_token_type(lex.TT_WITH)
    parser.advance()
    skip_indent(parser)

    pattern_parser = parser.pattern_parser
    branches = []
    # parser.assert_token_type(lex.TT_CASE)

    # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
    if parser.token_type == lex.TT_CASE:
        init_offside_layout(parser, parser.token)
        while pattern_parser.token_type == lex.TT_CASE:
            parser.advance_expected(lex.TT_CASE)
            pattern = _parse_pattern(parser)

            parser.advance_expected(lex.TT_ARROW)
            init_code_layout(parser, parser.token, parser.lex.TERM_CASE)
            body = parser.statements(parser.lex.TERM_CASE)

            branches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        parser.advance_expected(lex.TT_ARROW)
        init_code_layout(parser, parser.token)
        body = parser.statements(parser.lex.TERM_BLOCK)
        branches.append(list_node([pattern, body]))

    parser.advance_end()

    if len(branches) == 0:
        parse_error(parser, "Empty match expression", token)

    return node_2(lex.NT_MATCH, token, exp, list_node(branches))


def prefix_throw(parser, op, token):
    exp = parser.expression(0)
    return node_1(parser.lex.token_node_type(token), token, exp)


# FUNCTION STUFF################################

def _parse_func_pattern(parser, arg_terminator, guard_terminator):
    pattern = juxtaposition_as_tuple(parser.fun_pattern_parser, arg_terminator)
    args_type = pattern.node_type

    if args_type != lex.NT_TUPLE:
        parse_error(parser, "Invalid  syntax in function arguments", pattern)

    if parser.token_type == lex.TT_WHEN:
        parser.advance()
        guard = parser.guard_parser.terminated_expression(0, guard_terminator)
        pattern = node_2(lex.NT_WHEN, guard.token, pattern, guard)

    return pattern


def _parse_function_signature(parser):
    """
        signature can be one of
        arg1 arg2
        arg1 . arg2 ...arg3
        arg1 of T arg2 of T
        ()
        (arg1 arg2 of T ...arg3)
    """
    pattern = juxtaposition_as_tuple(
        parser.fun_signature_parser, parser.lex.TERM_FUN_SIGNATURE)
    skip_indent(parser)
    args_type = pattern.node_type
    if args_type != lex.NT_TUPLE:
        parse_error(parser, "Invalid  syntax in function signature", pattern)
    return pattern


def _parse_function_variants(parser, signature,
                             term_pattern, term_guard,
                             term_case_body, term_single_body):
    if parser.token_type == lex.TT_ARROW:
        parser.advance()
        init_code_layout(parser, parser.token, term_single_body)
        body = parser.statements(term_single_body)
        return create_function_variants(signature, body)

    # bind to different name for not confusing reading code
    # it serves as basenode for token factory functions
    token = signature.token
    parser.assert_token_type(lex.TT_CASE)

    init_offside_layout(parser, parser.token)

    funcs = []
    sig_args = signature.first()
    sig_arity = len(sig_args)

    while parser.token_type == lex.TT_CASE:
        parser.advance_expected(lex.TT_CASE)
        args = _parse_func_pattern(parser, term_pattern, term_guard)
        if args.node_type == lex.NT_WHEN:
            args_sig = args.first()
        else:
            args_sig = args
        if tuple_node_length(args_sig) != sig_arity:
            return parse_error(parser,
                               "Inconsistent clause arity" +
                               "with function signature",
                               args)

        parser.advance_expected(lex.TT_ARROW)
        init_code_layout(parser, parser.token, term_case_body)
        body = parser.statements(term_case_body)
        funcs.append(list_node([args, body]))

    return node_2(parser.lex.NT_FUN,
                  token,
                  empty_node(), list_node(funcs))


def _parse_function(parser, term_pattern,
                    term_guard, term_case_body, term_single_body):
    signature = _parse_function_signature(parser)
    funcs = _parse_function_variants(
        parser, signature, term_pattern,
        term_guard, term_case_body, term_single_body)
    return funcs


def _parse_named_function(parser, token):
    init_node_layout(parser, token)
    name = grab_name_or_operator(parser.name_parser)
    func = _parse_function(
        parser, parser.lex.TERM_FUN_PATTERN, parser.lex.TERM_FUN_GUARD, parser.lex.TERM_CASE, parser.lex.TERM_BLOCK)
    parser.advance_end()
    return name, func


def prefix_fun(parser, op, token):
    name, funcs = _parse_named_function(parser, token)
    return node_2(lex.NT_FUN, token, name, funcs)


def prefix_module_fun(parser, op, token):
    name, funcs = _parse_named_function(parser.expression_parser, token)
    return node_2(lex.NT_FUN, token, name, funcs)


def prefix_lambda(parser, op, token):
    init_node_layout(parser, token)
    func = _parse_function(
        parser, parser.lex.TERM_FUN_PATTERN, parser.lex.TERM_FUN_GUARD, parser.lex.TERM_CASE, parser.lex.TERM_BLOCK)
    parser.advance_end()
    return node_2(lex.NT_FUN, token, empty_node(), func)


###############################################################
# IMPORT STATEMENTS
###############################################################
def ensure_tuple(t):
    if t.node_type != lex.NT_TUPLE:
        return create_tuple_node(t, [t])
    return t


def stmt_from(parser, op, token):
    imported = parser.import_parser.terminated_expression(
        0, parser.lex.TERM_FROM_IMPORTED)
    parser.assert_token_types([lex.TT_IMPORT, lex.TT_HIDE])
    if parser.token_type == lex.TT_IMPORT:
        hiding = False
        ntype = lex.NT_IMPORT_FROM
    else:
        hiding = True
        ntype = lex.NT_IMPORT_FROM_HIDING

    parser.advance()
    if parser.token_type == lex.TT_WILDCARD:
        if hiding is True:
            return parse_error(parser,
                               "Invalid usage of hide"
                               "Symbol(s) expected",
                               token)

        names = empty_node()
        parser.advance()
    else:
        names = parser.import_names_parser.expression(0)
        parser.assert_node_types(names, [lex.NT_TUPLE, lex.NT_NAME, lex.NT_AS])
        names = ensure_tuple(names)
        if hiding is True:
            # hiding names can't have as binding
            parser.assert_types_in_nodes_list(names.first(), [lex.NT_NAME])

    return node_2(ntype, token, imported, names)


def stmt_import(parser, op, token):
    imported = parser.import_parser.terminated_expression(
        0, [lex.TT_LPAREN, lex.TT_HIDING])

    if parser.token_type == lex.TT_HIDING:
        ntype = lex.NT_IMPORT_HIDING
        hiding = True
        parser.advance()
    else:
        hiding = False
        ntype = lex.NT_IMPORT

    if parser.token_type == lex.TT_LPAREN:
        names = parser.import_names_parser.expression(0)
        parser.assert_node_types(names, [lex.NT_TUPLE, lex.NT_NAME, lex.NT_AS])
        names = ensure_tuple(names)
        if hiding is True:
            # hiding names can't have as binding
            parser.assert_types_in_nodes_list(names.first(), [lex.NT_NAME])
    else:
        if hiding is True:
            return parse_error(parser,
                               "Invalid usage of hide keyword."
                               " Symbol(s) expected", token)
        names = empty_node()

    return node_2(ntype, token, imported, names)


def stmt_export(parser, op, token):
    parser.assert_token_types([lex.TT_LPAREN, lex.TT_NAME])
    names = parser.import_names_parser.expression(0)
    parser.assert_node_types(names, [lex.NT_TUPLE, lex.NT_NAME])
    names = ensure_tuple(names)
    parser.assert_types_in_nodes_list(names.first(), [lex.NT_NAME])
    return node_1(lex.NT_EXPORT, token, names)


def symbol_or_name_value(parser, name):
    if name.node_type == lex.NT_SYMBOL:
        data = name.first()
        if data.node_type == lex.NT_NAME:
            return data.token_value
        elif data.node_type == lex.NT_STR:
            return strutil.unquote(data.token_value)
        else:
            assert False, "Invalid symbol"
    elif name.node_type == lex.NT_NAME:
        return name.token_value
    else:
        assert False, "Invalid name"


# TYPES ************************
def prefix_name_as_symbol(parser, op, token):
    name = node_0(parser.lex.token_node_type(token),
                        token)
    return create_symbol_node(token, name)


def symbol_list_to_arg_tuple(parser, token, symbols):
    args = []
    children = symbols.first()
    for child in children:
        assert child.node_type == lex.NT_SYMBOL
        name = child.first()
        args.append(name)

    return nodes.node_1(lex.NT_TUPLE, token, list_node(args))


def _symbols_to_args(parser, token, symbols):
    args = []
    for child in symbols:
        assert child.node_type == lex.NT_SYMBOL
        name = child.first()
        args.append(name)

    return nodes.node_1(lex.NT_TUPLE, token, list_node(args))


# DERIVE ################################
def _parse_tuple_of_names(parser, term):
    exp = parser.assert_any_of_terminated_expressions(
        0, [lex.NT_NAME, lex.NT_LOOKUP, lex.NT_TUPLE], term)
    if exp.node_type == lex.NT_TUPLE:
        parser.assert_types_in_nodes_list(
            exp.first(), [lex.NT_NAME, lex.NT_LOOKUP])
        return exp
    elif exp.node_type != lex.NT_TUPLE:
        return create_tuple_node(exp.token, [exp])


def _parse_union(parser, token, union_name):
    types = []
    init_offside_layout(parser, parser.token)
    parser.assert_token_type(lex.TT_CASE)
    while parser.token_type == lex.TT_CASE:
        parser.advance()
        _typename = grab_name(parser.type_parser)
        _type = _parse_type(parser, token, _typename, parser.lex.TERM_UNION_TYPE_ARGS)
        types.append(_type)

    if len(types) < 2:
        parse_error(
            parser, "Union type must have at least two constructors",
            parser.token)

    parser.advance_end()
    return nodes.node_2(lex.NT_UNION,
                        token, union_name, nodes.list_node(types))


def _parse_type(parser, token, typename, term):
    if parser.token_type == lex.TT_NAME:
        fields = juxtaposition_as_list(parser.type_parser, term)
    else:
        fields = empty_node()

    return nodes.node_2(lex.NT_TYPE,
                        token, typename, fields)


# TODO BETTER PARSE ERRORS HERE
def stmt_type(parser, op, token):
    init_node_layout(parser, token)
    typename = grab_name(parser.type_parser)
    skip_indent(parser)

    if parser.token_type == lex.TT_CASE:
        return _parse_union(parser, token, typename)

    _t = _parse_type(parser, token, typename, parser.lex.TERM_TYPE_ARGS)
    parser.advance_end()
    return _t


# TRAIT*************************
def symbol_operator_name(parser, op, token):
    name = node_0(parser.lex.token_node_type(token), token)
    return create_name_from_operator(token, name)


def grab_name(parser):
    parser.assert_token_type(lex.TT_NAME)
    name = _init_default_current_0(parser)
    parser.advance()
    return name


def grab_name_or_operator(parser):
    parser.assert_token_types(
        [lex.TT_NAME, lex.TT_OPERATOR, lex.TT_DOUBLE_COLON])
    token = parser.token
    name = _init_default_current_0(parser)
    if parser.token_type == lex.TT_OPERATOR:
        name = create_name_from_operator(token, name)
    elif parser.token_type == lex.TT_DOUBLE_COLON:
        name = create_name_node_s(name, "cons")

    parser.advance()
    return name


def _parser_trait_header(parser, token):
    type_parser = parser.type_parser
    name = grab_name(type_parser)
    parser.assert_token_type(lex.TT_FOR)
    parser.advance()
    instance_name = grab_name(type_parser)
    if parser.token_type == lex.TT_OF:
        parser.advance()
        constraints = _parse_tuple_of_names(
            parser.name_parser, parser.lex.TERM_METHOD_CONSTRAINTS)
    else:
        constraints = create_empty_list_node(token)
    skip_indent(parser)
    return name, instance_name, constraints


def stmt_trait(parser, op, token):
    init_node_layout(parser, token)
    name, instance_name, constraints = _parser_trait_header(parser, token)
    methods = []
    init_offside_layout(parser, parser.token)
    while parser.token_type == lex.TT_DEF:
        parser.advance_expected(lex.TT_DEF)
        method_name = grab_name_or_operator(parser)
        parser.assert_token_type(lex.TT_NAME)

        sig = juxtaposition_as_list(
            parser.method_signature_parser, parser.lex.TERM_METHOD_SIG)
        parser.assert_node_type(sig, lex.NT_LIST)
        if parser.token_type == lex.TT_ARROW:
            parser.advance()
            init_code_layout(parser, parser.token,
                             parser.lex.TERM_METHOD_DEFAULT_BODY)
            args = symbol_list_to_arg_tuple(parser, token, sig)
            body = parser.expression_parser.statements(
                parser.lex.TERM_METHOD_DEFAULT_BODY)
            default_impl = create_function_variants(args, body)
        else:
            default_impl = empty_node()

        methods.append(list_node([method_name, sig, default_impl]))
    parser.advance_end()
    return nodes.node_4(lex.NT_TRAIT,
                        token, name,
                        instance_name, constraints, list_node(methods))


def _parser_implement_header(parser):
    trait_name = parser.name_parser.assert_any_of_terminated_expressions(
        0, parser.lex.NODE_IMPLEMENT_NAME, parser.lex.TERM_BEFORE_FOR)
    parser.advance_expected(lex.TT_FOR)
    type_name = parser.name_parser.assert_any_of_terminated_expressions(
        0, parser.lex.NODE_IMPLEMENT_NAME, parser.lex.TERM_IMPL_HEADER)
    skip_indent(parser)
    return trait_name, type_name


def stmt_implement(parser, op, token):
    init_node_layout(parser, token)
    trait_name, type_name = _parser_implement_header(parser)

    methods = []
    if parser.token_type != lex.TT_DEF:
        parser.advance_end()
        return nodes.node_3(lex.NT_IMPLEMENT,
                            token,
                            trait_name, type_name, list_node(methods))

    init_offside_layout(parser, parser.token)
    while parser.token_type == lex.TT_DEF:
        parser.advance_expected(lex.TT_DEF)
        # creating converting method names to symbols
        # method_name = grab_name_or_operator(parser.name_parser)
        method_name = parser.name_parser.assert_expression(0, lex.NT_NAME)
        method_name = create_symbol_node_s(
            method_name.token, method_name.token_value)

        funcs = _parse_function(parser.expression_parser,
                                parser.lex.TERM_FUN_PATTERN,
                                parser.lex.TERM_FUN_GUARD,
                                parser.lex.TERM_IMPL_BODY,
                                parser.lex.TERM_IMPL_BODY)
        methods.append(list_node([method_name, funcs]))

    parser.advance_end()
    return nodes.node_3(lex.NT_IMPLEMENT, token,
                        trait_name, type_name, list_node(methods))


def stmt_extend(parser, op, token):
    init_node_layout(parser, token)
    type_name = parser.name_parser.assert_any_of_terminated_expressions(
        0, parser.lex.NODE_IMPLEMENT_NAME, parser.lex.TERM_BEFORE_WITH)
    skip_indent(parser)
    traits = []

    while parser.token_type == lex.TT_WITH:
        init_offside_layout(parser, parser.token)
        parser.advance_expected(lex.TT_WITH)
        trait_name = parser.name_parser.assert_any_of_terminated_expressions(
            0, parser.lex.NODE_IMPLEMENT_NAME, parser.lex.TERM_EXTEND_TRAIT)
        skip_indent(parser)
        if parser.token_type == lex.TT_ASSIGN:
            parser.advance()
            implementation = parser.terminated_expression(
                0, parser.lex.TERM_EXTEND_MIXIN_TRAIT)
        elif parser.token_type == lex.TT_DEF:
            init_offside_layout(parser, parser.token)
            methods = []

            while parser.token_type == lex.TT_DEF:
                parser.advance_expected(lex.TT_DEF)
                method_name = parser.name_parser.assert_expression(0, lex.NT_NAME)
                method_name = create_symbol_node_s(
                    method_name.token, method_name.token_value)

                funcs = _parse_function(parser.expression_parser,
                                        parser.lex.TERM_FUN_PATTERN, parser.lex.TERM_FUN_GUARD,
                                        parser.lex.TERM_EXTEND_BODY, parser.lex.TERM_EXTEND_BODY)
                methods.append(list_node([method_name, funcs]))
            implementation = list_node(methods)
        else:
            implementation = list_node([])
        # parser.advance_end()
        traits.append(list_node([trait_name, implementation]))

    parser.advance_end()
    return nodes.node_2(lex.NT_EXTEND,
                        token, type_name, list_node(traits))


# OPERATORS

def stmt_prefix(parser, op, token):
    op_node = parser.name_parser.assert_expression(0, lex.NT_NAME)
    func_node = parser.name_parser.assert_expression(0, lex.NT_NAME)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    scope = parser.current_scope()
    op = scope.get_custom_operator_or_create_new(op_value)
    parser.operators.set_prefix_function(op, prefix_nud_function, func_value)

def stmt_infixl(parser, op, token):
    return _meta_infix(parser, token, infix_led_function)


def stmt_infixr(parser, op, token):
    return _meta_infix(parser, token, infixr_led_function)


def _meta_infix(parser, token, infix_function):
    op_node = parser.name_parser.assert_expression(0, lex.NT_NAME)
    func_node = parser.name_parser.assert_expression(0, lex.NT_NAME)
    precedence_node = parser.name_parser.assert_expression(0, lex.NT_INT)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)
    try:
        precedence = strutil.string_to_int(precedence_node.token_value)
    except:
        return parse_error(parser,
                           "Invalid infix operator precedence",
                           precedence_node)

    scope = parser.current_scope()
    op = scope.get_custom_operator_or_create_new(op_value)
    parser.operators.set_infix_function(op,
                                        precedence, infix_function, func_value)
