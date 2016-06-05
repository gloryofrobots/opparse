import json


class BaseNode(object):

    def to_json(self):
        raise NotImplementedError()

    def to_json_string(self):
        d = self.to_json()
        return json.dumps(d, sort_keys=True, indent=2, separators=(',', ': '))


class EmptyNode(BaseNode):

    def __eq__(self, other):
        return self is other

    def to_json(self):
        return {'empty': True}


class Node(BaseNode):

    def __init__(self, ntype, token, children):
        self.node_type = ntype
        self.token = token

        self.token_type = token.type
        self.token_value = token.value
        self.token_position = token.position
        self.token_line = token.line
        self.token_column = token.column

        if children is not None:
            for child in children:
                assert is_node(child), child
            self.children = children
        else:
            self.children = []

        self.length = len(self.children)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False

        if self.node_type != other.node_type:
            return False

        if self.value != other.value:
            return False

        if self.length != other.length:
            return False

        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False

        return True

    def getchild(self, index):
        return self.children[index]

    def first(self):
        return self.getchild(0)

    def second(self):
        return self.getchild(1)

    def third(self):
        return self.getchild(2)

    def fourth(self):
        return self.getchild(3)

    def to_json(self):
        d = {
            "_ntype": self.node_type,
            "_value": self.token_value,
        }

        if self.length:
            d['children'] = map(lambda c: c.to_json(), self.children)

        return d


class ListNode(BaseNode):

    def __init__(self, elements):
        self.elements = elements

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, index):
        return self.elements.__getitem__(index)

    def __len__(self):
        return self.elements.__len__()

    def __getslice__(self, start, end):
        return self.elements.__getslice__(start, end)

    def __str__(self):
        return "ListNode(%s)" % (", ".join(map(str, self.elements)))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, ListNode):
            return False

        return self.elements == other.elements

    def to_json(self):
        return map(lambda el: el.to_json(), self.elements)

    def concat(self, other):
        assert isinstance(other, ListNode)
        elements = self.elements + other.elements
        return ListNode(elements)

    def head(self):
        return self.elements[0]

    def tail(self):
        return ListNode(self.elements[1:])

__EMPTY__ = EmptyNode()


def empty_node():
    return __EMPTY__


def is_empty_node(n):
    return n is __EMPTY__


def list_node(items):
    assert isinstance(items, list)
    for item in items:
        assert is_node(item), item
    return ListNode(items)


def is_list_node(node):
    return isinstance(node, ListNode)


def is_single_node(node):
    return isinstance(node, Node)


def is_node(node):
    return isinstance(node, BaseNode)


def node_blank(token):
    return Node(-1, token, None)


def node_0(ntype, token):
    return Node(ntype, token, None)


def node_1(ntype, token, child):
    return Node(ntype, token, [child])


def node_2(ntype, token, child1, child2):
    return Node(ntype, token, [child1, child2])


def node_3(ntype, token, child1, child2, child3):
    return Node(ntype, token, [child1, child2, child3])


def node_4(ntype, token, child1, child2, child3, child4):
    return Node(ntype, token, [child1, child2, child3, child4])
