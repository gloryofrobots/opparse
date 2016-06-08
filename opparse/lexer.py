from rply import LexerGenerator


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


class LexerError(Exception):
    """ Lexer error exception.

        pos:
            Position in the input line where the error occurred.
    """

    def __init__(self, pos):
        self.pos = pos


class Lexer:
    def __init__(self, lexicon, skip_whitespace):
        self.lexicon = lexicon
        self.lexer = create_generator(lexicon.RULES)
        self.stream = None

    def input(self, buf):
        self.stream = self.lexer.lex(buf)

    def token(self):

        """ Return the next token (a Token object) found in the
            input buffer. None is returned if the end of the
            buffer was reached.
            In case of a lexing error (the current chunk of the
            buffer matches no rule), a LexerError is raised with
            the position of the error.
        """

        from rply.lexer import LexingError
        try:
            return self._token()
        except StopIteration:
            return None
        except LexingError as e:
            pos = e.source_pos
            raise (UnknownTokenError(pos.idx))

    def _token(self):
        t = next(self.stream)
        # print tokens.token_type_to_str(t.name), t.value
        token = Token(t.name, t.value,
                      t.source_pos.idx,
                      t.source_pos.lineno, t.source_pos.colno)

        if token.type == -1:
            return self._token()

        return token

    def tokens(self):
        """
        Returns an iterator to the tokens found in the buffer.
        """

        while 1:
            tok = self.token()
            if tok is None:
                # ADD FAKE NEWLINE TO SUPPORT ONE LINE SCRIPT FILES
                yield Token(self.lexicon.TT_NEWLINE, "\n", -1, -1, 1)
                yield Token(self.lexicon.TT_ENDSTREAM, "", -1, -1, 1)
                break
            yield tok


##


def lexer(txt, lex):
    lx = Lexer(lex, False)
    lx.input(txt)
    return lx
