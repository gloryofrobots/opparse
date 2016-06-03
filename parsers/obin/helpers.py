import lexicon.ObinLexicon as lex
import lang_names

from opparse.parse.nodes import (
    node_0, node_1, node_2, node_3,
    node_position, node_line, node_column, is_list_node, node_value,
    list_node, empty_node)

from opparse.parse import tokens


def create_token_from_node(type, value, node):
    return tokens.newtoken(type, value,
                           node_position(node),
                           node_line(node), node_column(node))


def create_function_variants(args, body):
    # print "ARGS", args
    # print "BODY", body
    return list_node([list_node([args, body])])


def create_fun_simple_node(basenode, name, body):
    return create_fun_node(basenode, name,
                           create_function_variants(
                               create_tuple_node(
                                   basenode, [create_unit_node(basenode)]),
                               body))


def create_fun_node(basenode, name, funcs):
    return node_2(lex.NT_FUN,
                  create_token_from_node(lex.TT_STR, "fun", basenode),
                  name, funcs)


def create_partial_node(basenode, name):
    return create_call_node_s(basenode, lang_names.PARTIAL, [name])


def create_temporary_node(basenode, idx):
    return node_1(lex.NT_TEMPORARY,
                  create_token_from_node(lex.TT_UNKNOWN, "", basenode), idx)


def create_name_node_s(basenode, name):
    return node_0(lex.NT_NAME,
                  create_token_from_node(lex.TT_NAME, name, basenode))


def create_name_from_operator(basenode, op):
    return create_name_node_s(basenode, node_value(op))


def create_name_node(basenode, name):
    return create_name_node_s(basenode, name)


def create_str_node(basenode, strval):
    return node_0(lex.NT_STR,
                  create_token_from_node(lex.TT_STR, strval, basenode))


def create_symbol_node(basenode, name):
    return node_1(lex.NT_SYMBOL,
                  create_token_from_node(lex.TT_SHARP, "#", basenode), name)


def create_symbol_node_s(basenode, name):
    return node_1(lex.NT_SYMBOL,
                  create_token_from_node(lex.TT_SHARP, "#", basenode),
                  create_name_node_s(basenode, name))


def create_int_node(basenode, val):
    return node_0(lex.NT_INT,
                  create_token_from_node(lex.TT_INT, str(val), basenode))


def create_true_node(basenode):
    return node_0(lex.NT_TRUE,
                  create_token_from_node(lex.TT_TRUE, "true", basenode))


def create_false_node(basenode):
    return node_0(lex.NT_FALSE,
                  create_token_from_node(lex.TT_FALSE, "false", basenode))


def create_void_node(basenode):
    return node_0(lex.NT_VOID,
                  create_token_from_node(lex.TT_TRUE, "void", basenode))


def create_undefine_node(basenode, varname):
    return node_1(lex.NT_UNDEFINE,
                  create_token_from_node(lex.TT_UNKNOWN, "undefine", basenode),
                  varname)


def create_goto_node(label):
    return node_0(lex.NT_GOTO,
                  tokens.newtoken(lex.TT_UNKNOWN, str(label), -1, -1, -1))


def create_fenv_node(basenode):
    return node_0(lex.NT_FENV,
                  create_token_from_node(lex.TT_NAME, "___fenv", basenode))


def create_wildcard_node(basenode):
    return node_0(lex.NT_WILDCARD,
                  create_token_from_node(lex.TT_WILDCARD, "_", basenode))


def create_unit_node(basenode):
    return node_0(lex.NT_UNIT,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode))


# def create_tuple_with_unit_node(basenode):
# return create_tuple_node(basenode, node_0(lex.NT_UNIT,
# create_token_from_node(lex.TT_LPAREN, "(", basenode)))

def create_tuple_node(basenode, elements):
    return node_1(lex.NT_TUPLE,
                  create_token_from_node(lex.TT_LPAREN,
                                         "(", basenode), list_node(elements))


def create_tuple_node_from_list(basenode, elements):
    assert is_list_node(elements)
    return node_1(lex.NT_TUPLE,
                  create_token_from_node(lex.TT_LPAREN,
                                         "(", basenode), elements)


def create_list_node(basenode, items):
    return node_1(lex.NT_LIST,
                  create_token_from_node(lex.TT_LSQUARE,
                                         "[", basenode), list_node(items))


def create_list_node_from_list(basenode, items):
    assert is_list_node(items)
    return node_1(lex.NT_LIST,
                  create_token_from_node(lex.TT_LSQUARE, "[", basenode), items)


def create_empty_list_node(basenode):
    return node_1(lex.NT_LIST,
                  create_token_from_node(lex.TT_LSQUARE, "[", basenode),
                  list_node([]))


def create_empty_map_node(basenode):
    return node_1(lex.NT_MAP,
                  create_token_from_node(lex.TT_LCURLY, "{", basenode),
                  list_node([]))


def create_match_fail_node(basenode, val, idx):
    sym = create_symbol_node_s(basenode, val)
    return create_tuple_node(basenode,
                             [sym, create_temporary_node(basenode, idx)])
    # return create_call_node_s(basenode, val, [create_name_node(basenode,
    # var)])


def create_if_node(basenode, branches):
    return node_1(lex.NT_CONDITION,
                  create_token_from_node(lex.TT_IF,
                                         "if", basenode), list_node(branches))


def create_call_node(basenode, func, exps):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN,
                                         "(", basenode), func, exps)


def create_call_node_1(basenode, func, exp):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  func, list_node([exp]))


def create_call_node_2(basenode, func, exp1, exp2):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  func, list_node([exp1, exp2]))


def create_call_node_3(basenode, func, exp1, exp2, exp3):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  func, list_node([exp1, exp2, exp3]))


def create_call_node_s(basenode, funcname, exps):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  create_name_node_s(basenode, funcname),
                  list_node(exps))


def create_when_no_else_node(basenode, cond, body):
    return node_2(lex.NT_WHEN,
                  create_token_from_node(lex.TT_WHEN, "when", basenode),
                  cond, body)


# CALL TO OPERATOR FUNCS
# TODO MAKE IT CONSISTENT WITH OPERATOR REDECLARATION

def create_eq_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.EQ, [left, right])


def create_gt_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.GE, [left, right])


def create_kindof_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.KINDOF, [left, right])


def create_isnot_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.ISNOT, [left, right])


def create_is_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.IS, [left, right])


def create_elem_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.ELEM, [left, right])


def create_is_indexed_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_INDEXED, [val])


def create_is_dict_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_DICT, [val])


def create_is_empty_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_EMPTY, [val])


def create_is_seq_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_SEQ, [val])


def create_len_node(basenode, val):
    return create_call_node_s(basenode, lang_names.LEN, [val])


def create_delay_node(basenode, exp):
    return node_1(lex.NT_DELAY,
                  create_token_from_node(lex.TT_DELAY, "delay", basenode), exp)


def create_delayed_cons_node(basenode, left, right):
    return create_cons_node(basenode, left, create_delay_node(basenode, right))


def create_cons_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.CONS, [left, right])


##############################

def create_and_node(basenode, left, right):
    return node_2(lex.NT_AND,
                  create_token_from_node(lex.TT_AND, "and", basenode),
                  left, right)


def create_assign_node(basenode, left, right):
    return node_2(lex.NT_ASSIGN,
                  create_token_from_node(lex.TT_ASSIGN, "=", basenode),
                  left, right)


def create_head_node(basenode):
    return node_0(lex.NT_HEAD,
                  create_token_from_node(lex.TT_UNKNOWN, "", basenode))


def create_tail_node(basenode):
    return node_0(lex.NT_TAIL,
                  create_token_from_node(lex.TT_UNKNOWN, "", basenode))


def create_drop_node(basenode, count):
    return node_1(lex.NT_DROP,
                  create_token_from_node(lex.TT_UNKNOWN, "..", basenode),
                  count)


def create_lookup_node(basenode, left, right):
    return node_2(lex.NT_LOOKUP,
                  create_token_from_node(lex.TT_LSQUARE, "[", basenode),
                  left, right)


def create_bind_node(basenode, left, right):
    return node_2(lex.NT_BIND,
                  create_token_from_node(lex.TT_AT_SIGN, "@", basenode),
                  left, right)


def create_of_node(basenode, left, right):
    return node_2(lex.NT_OF,
                  create_token_from_node(lex.TT_OF, "of", basenode),
                  left, right)


def create_match_node(basenode, exp, branches):
    return node_2(lex.NT_MATCH,
                  create_token_from_node(lex.TT_MATCH, "match", basenode),
                  exp, list_node(branches))


def create_try_statement_node(basenode, exp, success, fail):
    return node_3(lex.NT_TRY,
                  create_token_from_node(lex.TT_TRY, "try", basenode),
                  list_node([exp, success]),
                  list_node([empty_node(), list_node([fail])]),
                  empty_node())
