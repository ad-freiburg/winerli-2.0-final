""" Johanna Götz """
""" Code partially adapted from Niklas Baumert's thesis code """


# Closely based on Niklas Baumert's bachelor's thesis code
class Entity:
    __slots__ = ('wikilink', '__relevance', 'specificity', 'categories',
                 'pronoun', 'score')

    def __init__(self, wikilink, relevance, specificity, categories, pronoun,
                 score=None):
        self.wikilink = wikilink
        self.__relevance = relevance
        self.specificity = specificity
        if score is not None:
            self.score = score
        else:
            self.score = relevance
        self.categories = categories
        self.pronoun = pronoun

    @property
    def relevance(self):
        return self.__relevance

    @relevance.setter
    def relevance(self, relevance):
        self.__relevance = relevance
        if self.score is None:
            self.score = relevance

    def __str__(self):
        return '(%s, %s, %s, %s, %s, %s)' % (
            self.wikilink, str(self.relevance), str(self.specificity),
            str(self.score), str(self.categories), str(self.pronoun)
        )

    def __repr__(self):
        return ('<Entity wikilink: %s, relevance: %s, specificity: %s, '
                + 'score: %s, categories: %s, pronoun: %s>') % (
                    self.wikilink, self.relevance, self.specificity,
                    self.score, repr(self.categories), self.pronoun
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.wikilink == other.wikilink and
                    self.relevance == other.relevance and
                    self.specificity == other.specificity and
                    self.score == other.score and
                    self.categories == other.categories and
                    self.pronoun == other.pronoun)
        return False

    def __lt__(self, other):
        if type(other) is type(self):
            return self.wikilink < other.wikilink
        raise TypeError("'<' not supported between instances of '{}' and '{}'".format(type(self), type(other)))

    def to_dict(self):
        return {'wikilink': self.wikilink, 'relevance': self.relevance,
                'specificity': self.specificity, 'score': self. score,
                'categories': self.categories, 'pronoun': self.pronoun}
