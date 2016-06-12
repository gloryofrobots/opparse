class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.token = None
        self.src = src

    def next_token(self):
        self.token = next(self.tokens)
        return self.token
