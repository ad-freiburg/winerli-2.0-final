""" Johanna Götz """


# Representing a wikilink in terms of the link, the link text
# and the corresponding tokens
class Wikilink:
    def __init__(self, wikilink='', linktext=None):
        self.wikilink = wikilink
        self.linktext = linktext
        self.tokens = []

    # Add a token
    def add_token(self, token):
        self.tokens.append(token)

    def __len__(self):
        return len(self.linktext)

    # The start position of this link
    def start_pos(self):
        try:
            return self.tokens[0].idx
        except KeyError:
            return None

    def __repr__(self):
        return '{wikilink: %s, linktext: %s, tokens: %s}' % (
            repr(self.wikilink), repr(self.linktext), repr(self.tokens)
        )
