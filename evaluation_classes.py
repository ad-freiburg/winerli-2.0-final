""" Johanna Götz """
""" Code partially taken and adapted from Niklas Baumert's thesis code """


# Taken from Niklas Baumert's evaluation code
class Token:
    __slots__ = ('word', 'pos', 'tag', 'link')

    def __init__(self, word, pos, tag, link):
        self.word = word
        self.pos = pos
        self.tag = tag
        self.link = link

    def __repr__(self):
        return '<Token word: %s pos: %s tag: %s link: %s>' % (
            self.word, self.pos, self.tag, self.link
        )


# Taken from Niklas Baumert's evaluation code and adjusted/extended
class Metric:
    __slots__ = ('_precision', '_recall', '_f1', 'tp', 'fp', 'fn', 'decimals')

    def __init__(self):
        self._precision = None
        self._recall = None
        self._f1 = None
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.decimals = 4

    # Calculate precision if necessary
    @property
    def precision(self):
        if self._precision is None:
            if (self.tp + self.fp) == 0:
                self._precision = 0
            else:
                self._precision = self.tp / (self.tp + self.fp)
        return round(self._precision, self.decimals)

    # Calculate recall if necessary
    @property
    def recall(self):
        if self._recall is None:
            if (self.tp + self.fn) == 0:
                self._recall = 0
            else:
                self._recall = self.tp / (self.tp + self.fn)
        return round(self._recall, self.decimals)

    # Calculate the F1 score if necessary
    @property
    def f1(self):
        if self._f1 is None:
            if (self.precision + self.recall) == 0:
                self._f1 = 0
            else:
                self._f1 = (2 * self.precision * self.recall) / (self.precision + self.recall)
        return round(self._f1, self.decimals)

    def print_metrics(self):
        print('True positives: %s;\tFalse positives: %s;\tFalse negatives: %s' % (self.tp, self.fp, self.fn))
        print('Precision:', self.precision)
        print('Recall:', self.recall)
        print('F1-Score:', self.f1)
        print()

    def __repr__(self):
        return '<Metric tp: %s fp: %s fn: %s>' % (self.tp, self.fp, self.fn)


# Store an evaluation result's values
class EvalVals:
    __slots__ = ('task', 'system', 'dataset', 'scoring', 'threshold',
                 'adjectives', 'numbers', 'metrics')

    def __init__(self, task, system, dataset, scoring, threshold, adjectives,
                 numbers, metrics):
        self.task = task
        self.system = system
        self.metrics = metrics
        self.dataset = dataset
        self.scoring = scoring
        self.threshold = threshold
        self.adjectives = adjectives
        self.numbers = numbers

    def __repr__(self):
        return 'EvalVals(%s, %s, %s, %s, %s, %s, %s, %s)' % (
            self.task, self.system, self.dataset, self.scoring, self.threshold,
            self.adjectives, self.numbers, self.metrics)
