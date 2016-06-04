from lexicon import ObinLexicon as lex
import opparse.lexer

from opparse.nodes import (
    node_0, node_1, node_2,
    node_position, node_line, node_column, is_list_node, node_value,
    list_node)


def create_token_from_node(type, value, node):
    return opparse.lexer.Token(type, value,
                               node_position(node),
                               node_line(node), node_column(node))


def create_function_variants(args, body):
    # print "ARGS", args
    # print "BODY", body
    return list_node([list_node([args, body])])


def create_fun_node(basenode, name, funcs):
    return node_2(lex.NT_FUN,
                  create_token_from_node(lex.TT_STR, "fun", basenode),
                  name, funcs)


def create_name_node_s(basenode, name):
    return node_0(lex.NT_NAME,
                  create_token_from_node(lex.TT_NAME, name, basenode))


def create_name_from_operator(basenode, op):
    return create_name_node_s(basenode, node_value(op))


def create_name_node(basenode, name):
    return create_name_node_s(basenode, name)


def create_symbol_node(basenode, name):
    return node_1(lex.NT_SYMBOL,
                  create_token_from_node(lex.TT_SHARP, "#", basenode), name)


def create_symbol_node_s(basenode, name):
    return node_1(lex.NT_SYMBOL,
                  create_token_from_node(lex.TT_SHARP, "#", basenode),
                  create_name_node_s(basenode, name))


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


def create_call_node_2(basenode, func, exp1, exp2):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  func, list_node([exp1, exp2]))


def create_call_node(basenode, funcname, exps):
    return node_2(lex.NT_CALL,
                  create_token_from_node(lex.TT_LPAREN, "(", basenode),
                  create_name_node_s(basenode, funcname),
                  list_node(exps))

