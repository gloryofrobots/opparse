from opparse.parse import *
from opparse.parse import nodes, tokens
from opparse.parse.nodes import (
    node_token as __ntok, node_0, node_1, node_2, node_3, list_node, empty_node)
from opparse.misc import strutil
from opparse.parse.parser import newparser
import lexicon.ObinLexicon as lex

TERM_BLOCK = [lex.TT_END]
TERM_EXP = [lex.TT_END_EXPR]

TERM_IF_BODY = [lex.TT_ELSE, lex.TT_ELIF]
TERM_IF_CONDITION = [lex.TT_THEN]

TERM_MATCH_EXPR = [lex.TT_WITH]
TERM_MATCH_PATTERN = [lex.TT_WITH]
TERM_CASE = [lex.TT_CASE] + TERM_BLOCK
# TERM_CATCH = [lex.TT_CATCH, lex.TT_FINALLY] + TERM_BLOCK
TERM_TRY = [lex.TT_CATCH, lex.TT_FINALLY]
TERM_CATCH_CASE = [lex.TT_CASE, lex.TT_FINALLY] + TERM_BLOCK
TERM_SINGLE_CATCH = [lex.TT_FINALLY] + TERM_BLOCK

TERM_LET = [lex.TT_IN]

TERM_PATTERN = [lex.TT_WHEN]
TERM_FUN_GUARD = [lex.TT_ARROW]
TERM_FUN_PATTERN = [lex.TT_WHEN, lex.TT_ARROW]
TERM_FUN_SIGNATURE = [lex.TT_ARROW, lex.TT_CASE]

TERM_CONDITION_BODY = [lex.TT_CASE] + TERM_BLOCK
TERM_BEFORE_FOR = [lex.TT_FOR]

TERM_BEFORE_WITH = [lex.TT_WITH]

TERM_TYPE_ARGS = TERM_BLOCK
TERM_UNION_TYPE_ARGS = [lex.TT_CASE] + TERM_BLOCK

TERM_METHOD_SIG = [lex.TT_DEF, lex.TT_ARROW] + TERM_BLOCK
TERM_METHOD_DEFAULT_BODY = [lex.TT_DEF] + TERM_BLOCK
TERM_METHOD_CONSTRAINTS = [lex.TT_DEF] + TERM_BLOCK
TERM_IMPL_BODY = [lex.TT_CASE, lex.TT_DEF] + TERM_BLOCK
TERM_IMPL_HEADER = [lex.TT_DEF] + TERM_BLOCK

TERM_EXTEND_TRAIT = [lex.TT_DEF, lex.TT_ASSIGN] + TERM_BLOCK
TERM_EXTEND_MIXIN_TRAIT = [lex.TT_WITH] + TERM_BLOCK

TERM_EXTEND_BODY = [lex.TT_CASE, lex.TT_DEF, lex.TT_WITH] + TERM_BLOCK

TERM_FROM_IMPORTED = [lex.TT_IMPORT, lex.TT_HIDE]

TERM_CONDITION_CONDITION = [lex.TT_ARROW]

NODE_FOR_NAME = [lex.NT_NAME]
NODE_FUNC_NAME = [lex.NT_NAME]
NODE_DOT = [lex.NT_NAME, lex.NT_INT]
NODE_IMPLEMENT_NAME = [lex.NT_NAME, lex.NT_IMPORTED_NAME]

LOOP_CONTROL_TOKENS = [lex.TT_END, lex.TT_ELSE, lex.TT_CASE]

LEVELS_MATCH = TERM_MATCH_EXPR
LEVELS_IF = [lex.TT_ELSE, lex.TT_ELIF]
LEVELS_TRY = [lex.TT_CATCH, lex.TT_FINALLY]
LEVELS_LET = [lex.TT_IN]

SKIP_JUXTAPOSITION = [lex.TT_JUXTAPOSITION]


def advance_end(parser):
    advance_expected_one_of(parser, TERM_BLOCK)


def is_wildcard_node(n):
    return node_type(n) == lex.NT_WILDCARD


def tuple_node_length(n):
    assert node_type(n) == lex.NT_TUPLE, lex.node_type_to_s(node_type(n))
    return len(node_first(n))



def _init_default_current_0(parser):
    return nodes.node_0(parser.lex.get_nt_for_node(parser.node), __ntok(parser.node))
# additional helpers
def infix_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infix_function, infix_function)


def infixr_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infixr_function, infix_function)


def prefix_operator(parser, ttype, prefix_function):
    op = get_or_create_operator(parser, ttype)
    operator_prefix(op, prefix_nud_function, prefix_function)


def prefix_nud_function(parser, op, node):
    exp = literal_expression(parser)
    # exp = expression(parser, 100)
    return create_call_node_s(node, op.prefix_function, [exp])


def led_infix_function(parser, op, node, left):
    exp = expression(parser, op.lbp)
    return create_call_node_s(node, op.infix_function, [left, exp])


def led_infixr_function(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return create_call_node_s(node, op.infix_function, [left, exp])







##############################################################
# INFIX
##############################################################

def infix_backtick_name(parser, op, node, left):
    funcname = strutil.cat_both_ends(nodes.node_value_s(node))
    if not funcname:
        return parse_error(parser, u"invalid variable name in backtick expression", node)
    funcnode = nodes.create_name_node_s(node, funcname)

    right = expression(parser, op.lbp)
    return nodes.create_call_node_2(node, funcnode, left, right)


# def infix_double_colon(parser, op, node, left):
#     right = rexpression(parser, op)
#     return nodes.create_cons_node(node, left, right)


def infix_triple_colon(parser, op, node, left):
    right = rexpression(parser, op)
    return nodes.create_delayed_cons_node(node, left, right)


def infix_spacedot(parser, op, node, left):
    right = expression(parser, op.lbp)
    return nodes.node_2(lex.NT_JUXTAPOSITION, __ntok(node), left, right)


def infix_juxtaposition(parser, op, node, left):
    right = base_expression(parser, op.lbp)
    return nodes.node_2(lex.NT_JUXTAPOSITION, __ntok(node), left, right)


def infix_dot(parser, op, node, left):
    if parser.token_type == lex.TT_INT:
        idx = _init_default_current_0(parser)
        advance(parser)
        return node_2(lex.NT_LOOKUP, __ntok(node), left, idx)

    symbol = grab_name(parser)
    return node_2(lex.NT_LOOKUP, __ntok(node), left, nodes.create_symbol_node(symbol, symbol))


def infix_lcurly(parser, op, node, left):
    items = []
    init_free_layout(parser, node, [lex.TT_RCURLY])
    if parser.token_type != lex.TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(
                parser, [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT, lex.TT_STR, lex.TT_MULTI_STR, lex.TT_CHAR, lex.TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expression(parser, 10)

            advance_expected(parser, lex.TT_ASSIGN)
            value = expression(parser, 0)

            items.append(list_node([key, value]))

            if parser.token_type != lex.TT_COMMA:
                break

            advance_expected(parser, lex.TT_COMMA)

    advance_expected(parser, lex.TT_RCURLY)
    return node_2(lex.NT_MODIFY, __ntok(node), left, list_node(items))


def infix_lsquare(parser, op, node, left):
    init_free_layout(parser, node, [lex.TT_RSQUARE])
    exp = expression(parser, 0)
    advance_expected(parser, lex.TT_RSQUARE)
    return node_2(lex.NT_LOOKUP, __ntok(node), left, exp)


def infix_name_pair(parser, op, node, left):
    check_token_type(parser, lex.TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)
    return node_2(parser.lex.get_nt_for_node(node), __ntok(node), left, name)


def infix_at(parser, op, node, left):
    ltype = nodes.node_token_type(left)
    if ltype != lex.TT_NAME:
        parse_error(parser, u"Bad lvalue in pattern binding", left)

    exp = expression(parser, 9)
    return node_2(lex.NT_BIND, __ntok(node), left, exp)


##############################################################
# INFIX
##############################################################


def prefix_indent(parser, op, node):
    return parse_error(parser, u"Invalid indentation level", node)


def prefix_nud(parser, op, node):
    exp = literal_expression(parser)
    return node_1(parser.lex.get_nt_for_node(node), __ntok(node), exp)


def itself(parser, op, node):
    return node_0(parser.lex.get_nt_for_node(node), __ntok(node))


def _parse_name(parser):
    if parser.token_type == lex.TT_SHARP:
        node = parser.node
        advance(parser)
        return _parse_symbol(parser, node)

    check_token_types(parser, [lex.TT_STR, lex.TT_MULTI_STR, lex.TT_NAME])
    node = parser.node
    advance(parser)
    return node_0(parser.lex.get_nt_for_node(node), __ntok(node))


def _parse_symbol(parser, node):
    check_token_types(parser, [lex.TT_NAME, lex.TT_MULTI_STR, lex.TT_STR, lex.TT_OPERATOR])
    exp = node_0(parser.lex.get_nt_for_node(parser.node), __ntok(parser.node))
    advance(parser)
    return node_1(parser.lex.get_nt_for_node(node), __ntok(node), exp)


def prefix_backtick_operator(parser, op, node):
    opname = strutil.cat_both_ends(nodes.node_value_s(node))
    if opname == "::":
        return nodes.create_name_node_s(node, lang_names.CONS)

    op = parser_find_operator(parser, opname)
    if op is None:
        return parse_error(parser, u"Invalid operator", node)
    if op.infix_function is None:
        return parse_error(parser, u"Expected infix operator", node)

    return nodes.create_name_node(node, op.infix_function)


def prefix_sharp(parser, op, node):
    return _parse_symbol(parser, node)


def prefix_delay(parser, op, node):
    exp = expression(parser, 0)
    return nodes.create_delay_node(node, exp)


# def prefix_backtick(parser, op, node):
#     val = strutil.cat_both_ends(nodes.node_value_s(node))
#     if not val:
#         return parse_error(parser, u"invalid variable name", node)
#     return nodes.create_name_node(node, val)


def symbol_wildcard(parser, op, node):
    return parse_error(parser, u"Invalid use of _ pattern", node)


# MOST complicated operator
# expressions (f 1 2 3) (2 + 3) (-1)
# tuples (1,2,3,4,5)
def layout_lparen(parser, op, node):
    init_free_layout(parser, node, [lex.TT_RPAREN])


def prefix_lparen(parser, op, node):
    if parser.token_type == lex.TT_RPAREN:
        advance_expected(parser, lex.TT_RPAREN)
        return nodes.create_unit_node(node)

    e = expression(parser, 0, [lex.TT_RPAREN])
    skip_end_expression(parser)

    if parser.token_type == lex.TT_RPAREN:
        advance_expected(parser, lex.TT_RPAREN)
        return e

    items = [e]
    advance_expected(parser, lex.TT_COMMA)

    if parser.token_type != lex.TT_RPAREN:
        while True:
            items.append(expression(parser, 0, [lex.TT_COMMA]))
            skip_end_expression(parser)
            if parser.token_type == lex.TT_RPAREN:
                break
            advance_expected(parser, lex.TT_COMMA)

    advance_expected(parser, lex.TT_RPAREN)
    return node_1(lex.NT_TUPLE, __ntok(node), list_node(items))


def layout_lsquare(parser, op, node):
    init_free_layout(parser, node, [lex.TT_RSQUARE])


def prefix_lsquare(parser, op, node):
    items = []
    if parser.token_type != lex.TT_RSQUARE:
        while True:
            items.append(expression(parser, 0))
            skip_end_expression(parser)

            if parser.token_type != lex.TT_COMMA:
                break

            advance_expected(parser, lex.TT_COMMA)

    advance_expected(parser, lex.TT_RSQUARE)
    return node_1(lex.NT_LIST, __ntok(node), list_node(items))


def on_bind_node(parser, key):
    if nodes.node_type(key) != lex.NT_NAME:
        parse_error(parser, u"Invalid bind name", key)
    if parser.token_type == lex.TT_OF:
        advance_expected(parser, lex.TT_OF)
        check_token_type(parser, lex.TT_NAME)
        typename = grab_name(parser)
        return nodes.create_of_node(key, key, typename), empty_node()

    advance_expected(parser, lex.TT_AT_SIGN)
    real_key, value = _parse_map_key_pair(
        parser, [lex.TT_NAME, lex.TT_SHARP, lex.TT_STR, lex.TT_MULTI_STR], None)

    # allow syntax like {var1@ key}
    if nodes.node_type(real_key) == lex.NT_NAME:
        real_key = nodes.create_symbol_node(real_key, real_key)

    bind_key = nodes.create_bind_node(key, key, real_key)
    return bind_key, value


def prefix_lcurly_type(parser, op, node):
    items = []
    if parser.token_type != lex.TT_RCURLY:
        while True:
            name = expression(parser, 0)
            skip_end_expression(parser)
            check_node_type(parser, name, lex.NT_SYMBOL)

            items.append(name)
            if parser.token_type != lex.TT_COMMA:
                break

            advance_expected(parser, lex.TT_COMMA)

    advance_expected(parser, lex.TT_RCURLY)
    return node_1(lex.NT_LIST, __ntok(node), list_node(items))


def layout_lcurly(parser, op, node):
    init_free_layout(parser, node, [lex.TT_RCURLY])


# this callback used in pattern matching
def prefix_lcurly_patterns(parser, op, node):
    return _prefix_lcurly(parser, op, node, [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT, lex.TT_MULTI_STR, lex.TT_STR, lex.TT_CHAR, lex.TT_FLOAT],
                          on_bind_node)


def prefix_lcurly(parser, op, node):
    return _prefix_lcurly(parser, op, node, [lex.TT_NAME, lex.TT_SHARP, lex.TT_INT, lex.TT_STR, lex.TT_MULTI_STR, lex.TT_CHAR, lex.TT_FLOAT],
                          on_bind_node)


def _parse_map_key_pair(parser, types, on_unknown):
    check_token_types(parser, types)
    # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
    key = expression(parser, 10)

    if parser.token_type == lex.TT_COMMA:
        value = empty_node()
    elif parser.token_type == lex.TT_RCURLY:
        value = empty_node()
    elif parser.token_type == lex.TT_ASSIGN:
        advance_expected(parser, lex.TT_ASSIGN)
        value = expression(parser, 0)
        skip_end_expression(parser)
    else:
        if on_unknown is None:
            parse_error(parser, u"Invalid map declaration syntax", parser.node)
        key, value = on_unknown(parser, key)

    return key, value


def _prefix_lcurly(parser, op, node, types, on_unknown):
    # on_unknown used for pattern_match in binds {NAME @ name = "Alice"}
    items = []
    if parser.token_type != lex.TT_RCURLY:
        while True:
            # TODO check it
            key, value = _parse_map_key_pair(parser, types, on_unknown)
            items.append(list_node([key, value]))

            if parser.token_type != lex.TT_COMMA:
                break

            advance_expected(parser, lex.TT_COMMA)

    advance_expected(parser, lex.TT_RCURLY)
    return node_1(lex.NT_MAP, __ntok(node), list_node(items))


def prefix_if(parser, op, node):
    init_node_layout(parser, node, LEVELS_IF)
    branches = []

    cond = expression(parser, 0, TERM_IF_CONDITION)
    advance_expected_one_of(parser, TERM_IF_CONDITION)
    init_code_layout(parser, parser.node, TERM_IF_BODY)

    body = statements(parser, TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    check_token_types(parser, TERM_IF_BODY)

    while parser.token_type == lex.TT_ELIF:
        advance_expected(parser, lex.TT_ELIF)

        cond = expression(parser, 0, TERM_IF_CONDITION)
        advance_expected_one_of(parser, TERM_IF_CONDITION)
        init_code_layout(parser, parser.node, TERM_IF_BODY)

        body = statements(parser, TERM_IF_BODY)
        check_token_types(parser, TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    advance_expected(parser, lex.TT_ELSE)
    init_code_layout(parser, parser.node, TERM_BLOCK)

    body = statements(parser, TERM_BLOCK)
    branches.append(list_node([empty_node(), body]))
    advance_end(parser)
    return node_1(lex.NT_CONDITION, __ntok(node), list_node(branches))


def prefix_let(parser, op, node):
    init_node_layout(parser, node, LEVELS_LET)
    init_code_layout(parser, parser.node, TERM_LET)
    letblock = statements(parser, TERM_LET)
    advance_expected(parser, lex.TT_IN)
    skip_indent(parser)
    init_code_layout(parser, parser.node)
    inblock = statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_2(lex.NT_LET, __ntok(node), letblock, inblock)


def prefix_try(parser, op, node):
    init_node_layout(parser, node, LEVELS_TRY)
    init_code_layout(parser, parser.node, TERM_TRY)

    trybody = statements(parser, TERM_TRY)
    catches = []

    check_token_type(parser, lex.TT_CATCH)
    advance(parser)
    skip_indent(parser)

    if parser.token_type == lex.TT_CASE:
        init_offside_layout(parser, parser.node)
        while parser.token_type == lex.TT_CASE:
            advance_expected(parser, lex.TT_CASE)
            # pattern = expressions(parser.pattern_parser, 0)
            pattern = _parse_pattern(parser)
            advance_expected(parser, lex.TT_ARROW)
            init_code_layout(parser, parser.node, TERM_CATCH_CASE)
            body = statements(parser, TERM_CATCH_CASE)
            catches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        advance_expected(parser, lex.TT_ARROW)
        init_code_layout(parser, parser.node, TERM_SINGLE_CATCH)
        body = statements(parser, TERM_SINGLE_CATCH)
        catches.append(list_node([pattern, body]))

    if parser.token_type == lex.TT_FINALLY:
        advance_expected(parser, lex.TT_FINALLY)
        advance_expected(parser, lex.TT_ARROW)
        init_code_layout(parser, parser.node)
        finallybody = statements(parser, TERM_BLOCK)
    else:
        finallybody = empty_node()

    advance_end(parser)

    return node_3(lex.NT_TRY, __ntok(node), trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expression(parser.pattern_parser, 0, TERM_PATTERN)
    if parser.token_type == lex.TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, TERM_FUN_GUARD)
        pattern = node_2(lex.NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def prefix_match(parser, op, node):
    init_node_layout(parser, node, LEVELS_MATCH)
    init_code_layout(parser, parser.node, TERM_MATCH_EXPR)

    exp = expression_with_optional_end_of_expression(
        parser, 0, TERM_MATCH_PATTERN)
    # skip_indent(parser)
    check_token_type(parser, lex.TT_WITH)
    advance(parser)
    skip_indent(parser)

    pattern_parser = parser.pattern_parser
    branches = []
    # check_token_type(parser, lex.TT_CASE)

    # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
    if parser.token_type == lex.TT_CASE:
        init_offside_layout(parser, parser.node)
        while pattern_parser.token_type == lex.TT_CASE:
            advance_expected(pattern_parser, lex.TT_CASE)
            pattern = _parse_pattern(parser)

            advance_expected(parser, lex.TT_ARROW)
            init_code_layout(parser, parser.node, TERM_CASE)
            body = statements(parser, TERM_CASE)

            branches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        advance_expected(parser, lex.TT_ARROW)
        init_code_layout(parser, parser.node)
        body = statements(parser, TERM_BLOCK)
        branches.append(list_node([pattern, body]))

    advance_end(parser)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    return node_2(lex.NT_MATCH, __ntok(node), exp, list_node(branches))


def prefix_throw(parser, op, node):
    exp = expression(parser, 0)
    return node_1(parser.lex.get_nt_for_node(node), __ntok(node), exp)


# FUNCTION STUFF################################

def _parse_func_pattern(parser, arg_terminator, guard_terminator):
    pattern = juxtaposition_as_tuple(parser.fun_pattern_parser, arg_terminator)
    args_type = nodes.node_type(pattern)

    if args_type != lex.NT_TUPLE:
        parse_error(parser, u"Invalid  syntax in function arguments", pattern)

    if parser.token_type == lex.TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, guard_terminator)
        pattern = node_2(lex.NT_WHEN, __ntok(guard), pattern, guard)

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
        parser.fun_signature_parser, TERM_FUN_SIGNATURE)
    skip_indent(parser)
    args_type = nodes.node_type(pattern)
    if args_type != lex.NT_TUPLE:
        parse_error(parser, u"Invalid  syntax in function signature", pattern)
    return pattern


def _parse_function_variants(parser, signature, term_pattern, term_guard, term_case_body, term_single_body):
    if parser.token_type == lex.TT_ARROW:
        advance(parser)
        init_code_layout(parser, parser.node, term_single_body)
        body = statements(parser, term_single_body)
        return nodes.create_function_variants(signature, body)

    # bind to different name for not confusing reading code
    # it serves as basenode for node factory functions
    node = signature
    check_token_type(parser, lex.TT_CASE)

    init_offside_layout(parser, parser.node)

    funcs = []
    sig_args = nodes.node_first(signature)
    sig_arity = len(sig_args)

    while parser.token_type == lex.TT_CASE:
        advance_expected(parser, lex.TT_CASE)
        args = _parse_func_pattern(parser, term_pattern, term_guard)
        if nodes.node_type(args) == lex.NT_WHEN:
            args_sig = nodes.node_first(args)
        else:
            args_sig = args
        if nodes.tuple_node_length(args_sig) != sig_arity:
            return parse_error(parser, u"Inconsistent clause arity with function signature", args)

        advance_expected(parser, lex.TT_ARROW)
        init_code_layout(parser, parser.node, term_case_body)
        body = statements(parser, term_case_body)
        funcs.append(list_node([args, body]))

    func = nodes.create_fun_node(node, empty_node(), list_node(funcs))

    call_list = []
    for arg in sig_args:
        ntype = nodes.node_type(arg)
        if ntype == lex.NT_OF or ntype == lex.NT_REST:
            arg = nodes.node_first(arg)
        call_list.append(arg)

    body = list_node(
        [nodes.create_call_node(node, func, list_node(call_list))])
    main_func = nodes.create_function_variants(signature, body)
    return main_func


def _parse_function(parser, term_pattern, term_guard, term_case_body, term_single_body):
    signature = _parse_function_signature(parser)
    funcs = _parse_function_variants(
        parser, signature, term_pattern, term_guard, term_case_body, term_single_body)
    return funcs


def _parse_named_function(parser, node):
    init_node_layout(parser, node)
    name = grab_name_or_operator(parser.name_parser)
    func = _parse_function(
        parser, TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_CASE, TERM_BLOCK)
    advance_end(parser)
    return name, func


def prefix_fun(parser, op, node):
    name, funcs = _parse_named_function(parser, node)
    return node_2(lex.NT_FUN, __ntok(node), name, funcs)


def prefix_module_fun(parser, op, node):
    name, funcs = _parse_named_function(parser.expression_parser, node)
    return node_2(lex.NT_FUN, __ntok(node), name, funcs)


def prefix_lambda(parser, op, node):
    init_node_layout(parser, node)
    func = _parse_function(
        parser, TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_CASE, TERM_BLOCK)
    advance_end(parser)
    return node_2(lex.NT_FUN, __ntok(node), empty_node(), func)


###############################################################
# MODULE STATEMENTS
###############################################################

def stmt_module(parser, op, node):
    name = expression(parser.name_parser, 0)
    check_node_type(parser, name, lex.NT_NAME)
    stmts, scope = parse_module(parser, TERM_BLOCK)
    advance_end(parser)
    return node_3(lex.NT_MODULE, __ntok(node), name, stmts, scope)


def _load_path_s(node):
    if nodes.node_type(node) == lex.NT_IMPORTED_NAME:
        return _load_path_s(nodes.node_first(node)) + ':' + nodes.node_value_s(nodes.node_second(node))
    else:
        return nodes.node_value_s(node)


def _load_module(parser, exp):
    # here module must be loaded with
    # something like this

    # if nodes.node_type(exp) == lex.NT_AS:
    #     import_name = nodes.node_second(exp)
    #     module_path = _load_path_s(nodes.node_first(exp))
    # elif nodes.node_type(exp) == lex.NT_IMPORTED_NAME:
    #     import_name = nodes.node_second(exp)
    #     module_path = _load_path_s(exp)
    # else:
    #     assert nodes.node_type(exp) == lex.NT_NAME
    #     import_name = exp
    #     module_path = nodes.node_value_s(exp)
    #
    # state = parser.close()
    # module = import_module_function(state.process, module_path)
    # parser.open(state)
    pass


def ensure_tuple(t):
    if nodes.node_type(t) != lex.NT_TUPLE:
        return nodes.create_tuple_node(t, [t])
    return t


def stmt_from(parser, op, node):
    imported = expression(parser.import_parser, 0, TERM_FROM_IMPORTED)
    check_token_types(parser, [lex.TT_IMPORT, lex.TT_HIDE])
    if parser.token_type == lex.TT_IMPORT:
        hiding = False
        ntype = lex.NT_IMPORT_FROM
    else:
        hiding = True
        ntype = lex.NT_IMPORT_FROM_HIDING

    advance(parser)
    if parser.token_type == lex.TT_WILDCARD:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", node)

        names = empty_node()
        advance(parser)
    else:
        names = expression(parser.import_names_parser, 0)
        check_node_types(parser, names, [lex.NT_TUPLE, lex.NT_NAME, lex.NT_AS])
        names = ensure_tuple(names)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [lex.NT_NAME])

    _load_module(parser, imported)
    return node_2(ntype, __ntok(node), imported, names)


def stmt_import(parser, op, node):
    imported = expression(parser.import_parser, 0, [lex.TT_LPAREN, lex.TT_HIDING])

    if parser.token_type == lex.TT_HIDING:
        ntype = lex.NT_IMPORT_HIDING
        hiding = True
        advance(parser)
    else:
        hiding = False
        ntype = lex.NT_IMPORT

    if parser.token_type == lex.TT_LPAREN:
        names = expression(parser.import_names_parser, 0)
        check_node_types(parser, names, [lex.NT_TUPLE, lex.NT_NAME, lex.NT_AS])
        names = ensure_tuple(names)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [lex.NT_NAME])
    else:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", node)
        names = empty_node()

    _load_module(parser, imported)
    return node_2(ntype, __ntok(node), imported, names)


def stmt_export(parser, op, node):
    check_token_types(parser, [lex.TT_LPAREN, lex.TT_NAME])
    names = expression(parser.import_names_parser, 0)
    check_node_types(parser, names, [lex.NT_TUPLE, lex.NT_NAME])
    names = ensure_tuple(names)
    check_list_node_types(parser, nodes.node_first(names), [lex.NT_NAME])
    return node_1(lex.NT_EXPORT, __ntok(node), names)


def symbol_or_name_value(parser, name):
    if nodes.node_type(name) == lex.NT_SYMBOL:
        data = nodes.node_first(name)
        if nodes.node_type(data) == lex.NT_NAME:
            return nodes.node_value(data)
        elif nodes.node_type(data) == lex.NT_STR:
            return strutil.unquote_w(nodes.node_value(data))
        else:
            assert False, "Invalid symbol"
    elif nodes.node_type(name) == lex.NT_NAME:
        return nodes.node_value(name)
    else:
        assert False, "Invalid name"


# TYPES ************************
def prefix_name_as_symbol(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_symbol_node(name, name)


def symbol_list_to_arg_tuple(parser, node, symbols):
    args = []
    children = nodes.node_first(symbols)
    for child in children:
        assert nodes.node_type(child) == lex.NT_SYMBOL
        name = nodes.node_first(child)
        args.append(name)

    return nodes.node_1(lex.NT_TUPLE, nodes.node_token(node), list_node(args))


def _symbols_to_args(parser, node, symbols):
    args = []
    for child in symbols:
        assert nodes.node_type(child) == lex.NT_SYMBOL
        name = nodes.node_first(child)
        args.append(name)

    return nodes.node_1(lex.NT_TUPLE, nodes.node_token(node), list_node(args))


# DERIVE ################################
def _parse_tuple_of_names(parser, term):
    exp = expect_expression_of_types(
        parser, 0, [lex.NT_NAME, lex.NT_IMPORTED_NAME, lex.NT_TUPLE], term)
    if nodes.node_type(exp) == lex.NT_TUPLE:
        check_list_node_types(
            parser, nodes.node_first(exp), [lex.NT_NAME, lex.NT_IMPORTED_NAME])
        return exp
    elif nodes.node_type(exp) != lex.NT_TUPLE:
        return nodes.create_tuple_node(exp, [exp])


def _parse_union(parser, node, union_name):
    types = []
    init_offside_layout(parser, parser.node)
    check_token_type(parser, lex.TT_CASE)
    while parser.token_type == lex.TT_CASE:
        advance(parser)
        _typename = grab_name(parser.type_parser)
        _type = _parse_type(parser, node, _typename, TERM_UNION_TYPE_ARGS)
        types.append(_type)

    if len(types) < 2:
        parse_error(
            parser, u"Union type must have at least two constructors", parser.node)

    advance_end(parser)
    return nodes.node_2(lex.NT_UNION, __ntok(node), union_name, nodes.list_node(types))


def _parse_type(parser, node, typename, term):
    if parser.token_type == lex.TT_NAME:
        fields = juxtaposition_as_list(parser.type_parser, term)
        args = symbol_list_to_arg_tuple(parser, parser.node, fields)
        body = list_node([nodes.create_fenv_node(parser.node)])
        construct_funcs = nodes.create_function_variants(args, body)
    else:
        fields = empty_node()
        construct_funcs = empty_node()

    return nodes.node_3(lex.NT_TYPE, __ntok(node), typename, fields, construct_funcs)


# TODO BETTER PARSE ERRORS HERE
def stmt_type(parser, op, node):
    init_node_layout(parser, node)
    typename = grab_name(parser.type_parser)
    skip_indent(parser)

    if parser.token_type == lex.TT_CASE:
        return _parse_union(parser, node, typename)

    _t = _parse_type(parser, node, typename, TERM_TYPE_ARGS)
    advance_end(parser)
    return _t


# TRAIT*************************
def symbol_operator_name(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_name_from_operator(node, name)


def grab_name(parser):
    check_token_type(parser, lex.TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)
    return name


def grab_name_or_operator(parser):
    check_token_types(parser, [lex.TT_NAME, lex.TT_OPERATOR, lex.TT_DOUBLE_COLON])
    name = _init_default_current_0(parser)
    if parser.token_type == lex.TT_OPERATOR:
        name = nodes.create_name_from_operator(name, name)
    elif parser.token_type == lex.TT_DOUBLE_COLON:
        name = nodes.create_name_node_s(name, lang_names.CONS)

    advance(parser)
    return name


def _parser_trait_header(parser, node):
    type_parser = parser.type_parser
    name = grab_name(type_parser)
    check_token_type(parser, lex.TT_FOR)
    advance(parser)
    instance_name = grab_name(type_parser)
    if parser.token_type == lex.TT_OF:
        advance(parser)
        constraints = _parse_tuple_of_names(
            parser.name_parser, TERM_METHOD_CONSTRAINTS)
    else:
        constraints = nodes.create_empty_list_node(node)
    skip_indent(parser)
    return name, instance_name, constraints


def stmt_trait(parser, op, node):
    init_node_layout(parser, node)
    name, instance_name, constraints = _parser_trait_header(parser, node)
    methods = []
    init_offside_layout(parser, parser.node)
    while parser.token_type == lex.TT_DEF:
        advance_expected(parser, lex.TT_DEF)
        method_name = grab_name_or_operator(parser)
        check_token_type(parser, lex.TT_NAME)

        sig = juxtaposition_as_list(
            parser.method_signature_parser, TERM_METHOD_SIG)
        check_node_type(parser, sig, lex.NT_LIST)
        if parser.token_type == lex.TT_ARROW:
            advance(parser)
            init_code_layout(parser, parser.node, TERM_METHOD_DEFAULT_BODY)
            args = symbol_list_to_arg_tuple(parser, node, sig)
            body = statements(
                parser.expression_parser, TERM_METHOD_DEFAULT_BODY)
            default_impl = nodes.create_function_variants(args, body)
        else:
            default_impl = empty_node()

        methods.append(list_node([method_name, sig, default_impl]))
    advance_end(parser)
    return nodes.node_4(lex.NT_TRAIT, __ntok(node), name, instance_name, constraints, list_node(methods))


def _parser_implement_header(parser):
    trait_name = expect_expression_of_types(
        parser.name_parser, 0, NODE_IMPLEMENT_NAME, TERM_BEFORE_FOR)
    advance_expected(parser, lex.TT_FOR)
    type_name = expect_expression_of_types(
        parser.name_parser, 0, NODE_IMPLEMENT_NAME, TERM_IMPL_HEADER)
    skip_indent(parser)
    return trait_name, type_name


def stmt_implement(parser, op, node):
    init_node_layout(parser, node)
    trait_name, type_name = _parser_implement_header(parser)

    methods = []
    if parser.token_type != lex.TT_DEF:
        advance_end(parser)
        return nodes.node_3(lex.NT_IMPLEMENT, __ntok(node), trait_name, type_name, list_node(methods))

    init_offside_layout(parser, parser.node)
    while parser.token_type == lex.TT_DEF:
        advance_expected(parser, lex.TT_DEF)
        # creating converting method names to symbols
        # method_name = grab_name_or_operator(parser.name_parser)
        method_name = expect_expression_of(parser.name_parser, 0, lex.NT_NAME)
        method_name = nodes.create_symbol_node_s(
            method_name, nodes.node_value_s(method_name))

        funcs = _parse_function(parser.expression_parser,
                                TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_IMPL_BODY, TERM_IMPL_BODY)
        methods.append(list_node([method_name, funcs]))

    advance_end(parser)
    return nodes.node_3(lex.NT_IMPLEMENT, __ntok(node), trait_name, type_name, list_node(methods))


def stmt_extend(parser, op, node):
    init_node_layout(parser, node)
    type_name = expect_expression_of_types(
        parser.name_parser, 0, NODE_IMPLEMENT_NAME, TERM_BEFORE_WITH)
    skip_indent(parser)
    traits = []

    while parser.token_type == lex.TT_WITH:
        init_offside_layout(parser, parser.node)
        advance_expected(parser, lex.TT_WITH)
        trait_name = expect_expression_of_types(
            parser.name_parser, 0, NODE_IMPLEMENT_NAME, TERM_EXTEND_TRAIT)
        skip_indent(parser)
        if parser.token_type == lex.TT_ASSIGN:
            advance(parser)
            implementation = expression(parser, 0, TERM_EXTEND_MIXIN_TRAIT)
        elif parser.token_type == lex.TT_DEF:
            init_offside_layout(parser, parser.node)
            methods = []

            while parser.token_type == lex.TT_DEF:
                advance_expected(parser, lex.TT_DEF)
                method_name = expect_expression_of(
                    parser.name_parser, 0, lex.NT_NAME)
                method_name = nodes.create_symbol_node_s(
                    method_name, nodes.node_value_s(method_name))

                funcs = _parse_function(parser.expression_parser,
                                        TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_EXTEND_BODY, TERM_EXTEND_BODY)
                methods.append(list_node([method_name, funcs]))
            implementation = list_node(methods)
        else:
            implementation = list_node([])
        # advance_end(parser)
        traits.append(list_node([trait_name, implementation]))

    advance_end(parser)
    return nodes.node_2(lex.NT_EXTEND, __ntok(node), type_name, list_node(traits))


# OPERATORS

def stmt_prefix(parser, op, node):
    op_node = expect_expression_of(parser.name_parser, 0, lex.NT_NAME)
    func_node = expect_expression_of(parser.name_parser, 0, lex.NT_NAME)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_prefix(op, prefix_nud_function, func_value)

    parser_current_scope_add_operator(parser, op_value, op)


def stmt_infixl(parser, op, node):
    return _meta_infix(parser, node, led_infix_function)


def stmt_infixr(parser, op, node):
    return _meta_infix(parser, node, led_infixr_function)


def _meta_infix(parser, node, infix_function):
    op_node = expect_expression_of(parser.name_parser, 0, lex.NT_NAME)
    func_node = expect_expression_of(parser.name_parser, 0, lex.NT_NAME)
    precedence_node = expect_expression_of(parser.name_parser, 0, lex.NT_INT)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)
    try:
        precedence = strutil.string_to_int(nodes.node_value_s(precedence_node))
    except:
        return parse_error(parser, u"Invalid infix operator precedence", precedence_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_infix(op, precedence, infix_function, func_value)
    parser_current_scope_add_operator(parser, op_value, op)
