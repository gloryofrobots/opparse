import operator

from opparse import plist


def newnode(ntype, token, children):
    if children is not None:
        for child in children:
            assert is_node(child), child
        return (
            ntype, token, children,
            token.type
        )
    else:
        return (
            ntype, token, [],
            token.type
        )


def empty_node():
    return None


def is_empty_node(n):
    return n is None


def list_node(items):
    assert isinstance(items, list)
    for item in items:
        assert is_node(item), item
    return plist.plist(items)


# TODO THIS IS SILLY IMPLEMENT IT AS WRAPS
def is_list_node(node):
    return plist.islist(node)


def is_single_node(node):
    return isinstance(node, tuple) and len(node) == 4


def is_node(node):
    return is_list_node(node) or is_single_node(node) \
           or is_scope_node(node) or is_int_node(node) or is_empty_node(node)


def is_scope_node(node):
    from opparse.parser import ParserScope
    return isinstance(node, ParserScope)


def is_int_node(node):
    return isinstance(node, int)


def node_equal(node1, node2):
    assert is_node(node1) and is_node(node2), (node1, node2)

    if is_list_node(node1) and is_list_node(node2):
        return plist.equal_with(node1, node2, node_equal)

    if is_list_node(node1) or is_list_node(node2):
        return False

    #################################################

    if is_empty_node(node1) and is_empty_node(node2):
        return True

    if is_empty_node(node1) or is_empty_node(node2):
        return False

    #################################################

    if is_int_node(node1) and is_int_node(node2):
        return node1 == node2

    if is_int_node(node1) or is_int_node(node2):
        return False

    #################################################

    if node_type(node1) != node_type(node2):
        return False

    if node_value(node1) != node_value(node2):
        return False

    return plist.equal_with(node_children(node1),
                            node_children(node2), node_equal)


def node_blank(token):
    return newnode(-1, token, None)


def node_0(ntype, token):
    return newnode(ntype, token, None)


def node_1(ntype, token, child):
    return newnode(ntype, token, [child])


def node_2(ntype, token, child1, child2):
    return newnode(ntype, token, [child1, child2])


def node_3(ntype, token, child1, child2, child3):
    return newnode(ntype, token, [child1, child2, child3])


def node_4(ntype, token, child1, child2, child3, child4):
    return newnode(ntype, token, [child1, child2, child3, child4])


def node_type(node):
    return operator.getitem(node, 0)


def node_token(node):
    return operator.getitem(node, 1)


def node_children(node):
    return operator.getitem(node, 2)


def node_token_type(node):
    return node_token(node).type


def node_arity(node):
    return len(node_children(node))


def node_getchild(node, index):
    return node_children(node)[index]


def node_first(node):
    return node_getchild(node, 0)


def node_second(node):
    return node_getchild(node, 1)


def node_third(node):
    return node_getchild(node, 2)


def node_fourth(node):
    return node_getchild(node, 3)


def node_value(node):
    return node_token(node).value


def node_position(node):
    return node_token(node).position


def node_line(node):
    return node_token(node).line


def node_column(node):
    return node_token(node).column


def node_to_d(node):
    if is_empty_node(node):
        return {'empty': True}
    elif is_list_node(node):
        return [node_to_d(child) for child in node]
    elif is_scope_node(node):
        return {'scope': True}
    elif is_int_node(node):
        return {'intValue': node}
    else:
        d = {
            "_ntype": node_type(node) if node_type(node) != -1 else "",
            "_value": node_value(node),
            # "_line": node_line(node)
        }

        if node_children(node):
            d['children'] = [node_to_d(child) for child in node_children(node)]

        return d


def node_to_string(node):
    import json
    d = node_to_d(node)
    return json.dumps(d, sort_keys=True, indent=2, separators=(',', ': '))
