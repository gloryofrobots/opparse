class Token:

    def __init__(self, type, val, pos, line, column):
        assert isinstance(val, str)
        assert isinstance(pos, int)
        assert isinstance(line, int)
        assert isinstance(column, int)
        self.type = type
        self.val = val
        self.pos = pos
        self.line = line
        self.column = column
        self._hash_ = None

    def __hash__(self):
        if not self._hash_:
            self._hash_ = self._compute_hash_()

        return self._hash_

    def _compute_hash_(self):
        x = 0x345678
        for item in [self.val, self.pos, self.line, self.column]:
            y = hash(item)
            x = ((1000003 * x) ^ y)
        return x

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False

        if self.type != other.type:
            return False
        if self.val != other.val:
            return False

        if self.pos != other.pos:
            return False

        return True

    def __str__(self):
        return "Token(%s, %s, %d, %d)" % (str(self.type),
                                          self.val,
                                          self.line,
                                          self.column)

    def __repr__(self):
        return self.__str__()


def newtoken(type, val, pos, line, column):
    return Token(type, val, pos, line, column)


def newtoken_without_meta(type, val):
    return newtoken(type, val, -1, -1, -1)


def token_type(token):
    return token.type


def token_value(token):
    return token.val


def token_position(token):
    return token.pos


def token_line(token):
    return token.line


def token_column(token):
    return token.column

# indentation level
def token_level(token):
    return token_column(token) - 1
