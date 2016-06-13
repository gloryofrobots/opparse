from rply import LexerGenerator
from rply.lexer import LexingError

class Token:
    def __init__(self, type, val, pos, line, column):
        assert isinstance(val, str), val
        assert isinstance(pos, int)
        assert isinstance(line, int)
        assert isinstance(column, int)
        self.type = type
        self.value = val
        self.position = pos
        self.line = line
        self.column = column


        # indentation level
        self.level = self.column - 1
        self._hash_ = None

    def __hash__(self):
        if not self._hash_:
            self._hash_ = self._compute_hash_()

        return self._hash_

    def _compute_hash_(self):
        x = 0x345678
        for item in [self.value, self.position, self.line, self.column]:
            y = hash(item)
            x = ((1000003 * x) ^ y)
        return x

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False

        if self.type != other.type:
            return False
        if self.value != other.value:
            return False

        if self.position != other.position:
            return False

        return True

    def __str__(self):
        return "Token(%s, %s, %d, %d)" % (str(self.type),
                                          self.value,
                                          self.line,
                                          self.column)

    def __repr__(self):
        return self.__str__()


def create_generator(rules):
    lg = LexerGenerator()
    for rule in rules:
        lg.add(rule[1], rule[0])
    lexer = lg.build()
    return lexer


class UnknownTokenError(Exception):
    def __init__(self, position):
        self.position = position


class Lexer:
    def __init__(self, lexicon, txt):
        self.lexicon = lexicon
        self.lexer = create_generator(lexicon.RULES)
        self.stream = self.lexer.lex(txt)

    def token(self):
        try:
            return self._token()
        except StopIteration:
            return None
        except LexingError as e:
            pos = e.source_pos
            raise (UnknownTokenError(pos.idx))

    def _token(self):
        t = next(self.stream)
        token = Token(t.name, t.value,
                      t.source_pos.idx,
                      t.source_pos.lineno, t.source_pos.colno)

        if token.type == -1:
            return self._token()

        return token

    def as_list(self):
        tokens  = []
        while True:
            tok = self.token()
            if tok is None:
                tokens.append(Token(self.lexicon.TT_NEWLINE, "\n", -1, -1, 1))
                tokens.append(Token(self.lexicon.TT_ENDSTREAM, "", -1, -1, 1))
                break
            tokens.append(tok)

        return tokens

    def as_generator(self):
        """
        Returns an iterator to the tokens found in the buffer.
        """

        while 1:
            tok = self.token()
            if tok is None:
                # ADD FAKE NEWLINE TO SUPPORT ONE LINE SCRIPT FILES
                yield Token(self.lexicon.TT_ENDSTREAM, "", -1, -1, 1)
                break
            yield tok
