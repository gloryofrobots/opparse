import operator


class PList(object):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __hash__(self):
        return foldl(lambda el, acc: (1000003 * acc) ^ hash(el),
                     0x345678, self)

    def __iter__(self):
        cur = self
        while not is_empty(cur):
            yield head(cur)
            cur = cur.tail

    def __getitem__(self, index):
        assert isinstance(index, int)
        return nth(self, index)

    def __len__(self):
        return length(self)

    def __getslice__(self, start, end):
        return slice(self, start, end)

    def __str__(self):
        els = []
        cur = self
        while True:
            if is_empty(cur):
                break
            els.append(str(head(cur)))
            cur = cur.tail
        return "Plist([%s])" % (", ".join(els))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, PList):
            return False

        if is_empty(other) and is_empty(self):
            return True

        return equal(self, other)

    def to_l(self):
        return [i for i in self]


__EMPTY__ = PList(None, None)


def empty():
    return __EMPTY__


# def to_tuple(pl):
#     return tuple(pl.to_l())


def foldl(func, acc, pl):
    type_check(pl)
    if is_empty(pl):
        return acc

    return foldl(func,
                 func(head(pl), acc),
                 tail(pl))


def foldr(func, acc, pl):
    type_check(pl)
    if is_empty(pl):
        return acc

    return func(head(pl),
                foldr(func, acc, tail(pl)))


def is_empty(pl):
    return pl is __EMPTY__


def head(pl):
    type_check(pl)
    return pl.head


def type_check(pl):
    assert isinstance(pl, PList)

def tail(pl):
    type_check(pl)
    return pl.tail


def split(pl):
    type_check(pl)
    return head(pl), tail(pl)


def _length_foldl(el, acc):
    return acc + 1


def length(pl):
    type_check(pl)
    return foldl(_length_foldl, 0, pl)


def cons(v, pl):
    type_check(pl)
    return PList(v, pl)


def cons_n_list(items, pl):
    type_check(pl)
    head = pl
    for item in reversed(items):
        head = cons(item, head)
    return head


def append(pl, v):
    type_check(pl)
    return insert(pl, length(pl), v)


def concat(pl1, pl2):
    type_check(pl1)
    type_check(pl2)
    return foldr(cons, pl2, pl1)


def pop(pl):
    type_check(pl)
    return pl.tail


def take(pl, count):
    type_check(pl)
    if count <= 0:
        return empty()

    if is_empty(pl):
        raise IndexError(count)
    return cons(head(pl), take(pop(pl), count - 1))


def drop(pl, count):
    type_check(pl)
    if count == 0:
        return pl
    if is_empty(pl):
        raise IndexError(count)

    return drop(tail(pl), count - 1)


##############################################

def _slice(pl, index, start, end):
    if is_empty(pl):
        raise IndexError((index, start, end))

    if index < start:
        return _slice(tail(pl), index + 1, start, end)

    if index < end:
        return cons(head(pl), _slice(tail(pl), index + 1, start, end))

    return empty()


def slice(pl, start, end):
    type_check(pl)
    if start == end:
        return empty()

    assert (start >= 0, "Invalid slice : start < 0")
    assert (end > start, "Invalid slice : end <= start")
    assert (end > 0, "Invalid slice : end <= 0 start")

    # return take(drop(pl, start), end - 1)
    return _slice(pl, 0, start, end)


##############################################
__ABSENT__ = object()


def _nth(pl, index):
    if index == 0:
        return head(pl)
    if is_empty(pl):
        return __ABSENT__
    return _nth(tail(pl), index - 1)


def nth(pl, index):
    type_check(pl)
    v = _nth(pl, index)
    if v is __ABSENT__:
        raise IndexError(index)


##############################################

def _nth_tail(pl, index):
    if index == 0:
        return tail(pl)
    if is_empty(pl):
        return __ABSENT__
    return _nth_tail(tail(pl), index - 1)


def nth_tail(pl, index):
    type_check(pl)
    return _nth_tail(pl, index)


def insert(pl, index, v):
    type_check(pl)
    if index == 0:
        return cons(v, pl)

    if is_empty(pl):
        raise IndexError((index,v))

    return PList(head(pl), insert(tail(pl), index - 1, v))


def update(pl, index, v):
    type_check(pl)
    if index == 0:
        return cons(v, tail(pl))

    if is_empty(tail(pl)):
        raise IndexError((index,v))

    return PList(head(pl), update(tail(pl), index - 1, v))


def remove_all(pl, v):
    type_check(pl)
    if is_empty(pl):
        return pl

    if v == head(pl):
        l = remove_all(tail(pl), v)
        return l

    l = PList(head(pl), remove_all(tail(pl), v))
    return l


def remove(pl, v):
    type_check(pl)
    if is_empty(pl):
        raise IndexError(v)

    if v == head(pl):
        return tail(pl)

    return PList(head(pl), remove(tail(pl), v))


########################################################################

def contains_with(pl, v, condition):
    type_check(pl)
    if is_empty(pl):
        return False

    if condition(v, head(pl)):
        return True

    return contains_with(tail(pl), v, condition)


def contains(pl, v):
    return contains_with(pl, v, operator.eq)

########################################################################

def find_with(pl, v, condition):
    type_check(pl)
    if is_empty(pl):
        raise ValueError(v)

    if condition(v, head(pl)):
        return head(pl)

    return find_with(tail(pl), v, condition)


def find(pl, v):
    return contains_with(pl, v, operator.eq)

############################################################

def contains_split(pl, v):
    type_check(pl)
    if is_empty(pl):
        return False, empty()

    if operator.eq(v, head(pl)):
        return True, tail(pl)

    return contains_split(tail(pl), v)


def _contains_list(pl1, pl2):
    if is_empty(pl2):
        return True
    if is_empty(pl1):
        return False

    if not operator.eq(head(pl1), head(pl2)):
        return False
    else:
        return _contains_list(tail(pl1), tail(pl2))


def contains_list(pl1, pl2):
    if is_empty(pl2):
        return True
    if is_empty(pl1):
        return False

    find, pl1_tail = contains_split(pl1, head(pl2))
    if not find:
        return False
    return _contains_list(pl1_tail, tail(pl2))


def equal_with(pl1, pl2, condition):
    if is_empty(pl2) and is_empty(pl1):
        return True
    if is_empty(pl1):
        return False
    if is_empty(pl2):
        return False

    if not condition(head(pl1), head(pl2)):
        return False
    else:
        return equal_with(tail(pl1), tail(pl2), condition)


def equal(pl1, pl2):
    return equal_with(pl1, pl2, operator.eq)


######################################################

def _substract(pl1, pl2, result):
    if is_empty(pl1):
        return result

    if not contains(pl2, head(pl1)):
        return _substract(tail(pl1), pl2, cons(head(pl1), result))
    else:
        return _substract(tail(pl1), pl2, result)


def substract(pl1, pl2):
    type_check(pl1)
    type_check(pl2)
    return reverse(_substract(pl1, pl2, empty()))


######################################################

def index(pl, elem):
    type_check(pl)
    cur = pl
    idx = 0
    while True:
        if is_empty(cur):
            return -1
        if operator.eq(head(cur), elem):
            return idx
        idx += 1
        cur = cur.tail


def fmap(func, pl):
    type_check(pl)
    if is_empty(pl):
        return empty()

    return cons(func(head(pl)), fmap(func, tail(pl)))


def each(func, pl):
    type_check(pl)
    if is_empty(pl):
        return None

    result = func(head(pl))
    if result is not None:
        return result

    return each(func, tail(pl))


##############################################################

def _reverse_acc(pl, result):
    if is_empty(pl):
        return result
    return _reverse_acc(tail(pl), cons(head(pl), result))


def reverse(pl):
    type_check(pl)
    return _reverse_acc(pl, empty())


##############################################################
def islist(l):
    return isinstance(l, PList)

def plist_vec(process, vec):
    items = vec.to_l()
    return plist(items)


def plist_tuple(process, tupl):
    items = tupl.to_l()
    return plist(items)


def plist(items):
    lst = empty()
    for item in reversed(items):
        lst = cons(item, lst)
    return lst


def plist1(item):
    return cons(item, empty())
