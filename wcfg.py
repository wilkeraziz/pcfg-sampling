"""
@author wilkeraziz
"""

from collections import defaultdict, deque
from symbol import is_terminal
from rule import Rule
from math import log


class WCFG(object):

    def __init__(self, rules=[]):
        self._rules = []
        self._rules_by_lhs = defaultdict(list)
        self._terminals = set()
        self._nonterminals = set()
        for rule in rules:
            self.add(rule)

    def add(self, rule):
        self._rules.append(rule)
        self._rules_by_lhs[rule.lhs].append(rule)
        self._nonterminals.add(rule.lhs)
        for s in rule.rhs:
            if is_terminal(s):
                self._terminals.add(s)
            else:
                self._nonterminals.add(s)

    def update(self, rules):
        for rule in rules:
            self.add(rule)

    @property
    def nonterminals(self):
        return self._nonterminals

    @property
    def terminals(self):
        return self._terminals

    def __len__(self):
        return len(self._rules)

    def __getitem__(self, lhs):
        return self._rules_by_lhs.get(lhs, frozenset())

    def get(self, lhs, default=frozenset()):
        return self._rules_by_lhs.get(lhs, frozenset())

    def can_rewrite(self, lhs):
        """Whether a given nonterminal can be rewritten.

        This may differ from ``self.is_nonterminal(symbol)`` which returns whether a symbol belongs
        to the set of nonterminals of the grammar.
        """
        return lhs in self._rules_by_lhs

    def __iter__(self):
        return iter(self._rules)
    
    def iteritems(self):
        return self._rules_by_lhs.iteritems()
    
    def __str__(self):
        lines = []
        for lhs, rules in self.iteritems():
            for rule in rules:
                lines.append(str(rule))
        return '\n'.join(lines)


def count_derivations(wcfg, root):
    
    def recursion(derivation, projection, Q, wcfg, counts):
        #print 'd:', '|'.join(str(r) for r in derivation)
        #print 'p:', projection
        #print 'Q:', Q
        if Q:
            sym = Q.popleft()
            #print ' pop:', sym
            if is_terminal(sym):
                recursion(derivation, [sym] + projection, Q, wcfg, counts)
            else:
                for rule in wcfg[sym]:
                    #print '  rule:', rule
                    QQ = deque(Q)
                    QQ.extendleft(rule.rhs)
                    recursion(derivation + [rule], projection, QQ, wcfg, counts)
        else:
            counts['d'][tuple(derivation)] += 1
            counts['p'][tuple(projection)] += 1

    
    counts = {'d': defaultdict(int), 'p': defaultdict(int)}
    recursion([], [], deque([root]), wcfg, counts)
    return counts


def read_grammar_rules(istream, transform=log, strip_quotes=False):
    """
    Reads grammar rules in cdec format.


    >>> import math
    >>> istream = ['[S] ||| [X] ||| 1.0', '[X] ||| [X] [X] ||| 0.5'] + ['[X] ||| %d ||| 0.1' % i for i in range(1,6)]
    >>> rules = list(read_grammar_rules(istream, transform=log))
    >>> rules
    [[S] -> [X] (0.0), [X] -> [X] [X] (-0.69314718056), [X] -> 1 (-2.30258509299), [X] -> 2 (-2.30258509299), [X] -> 3 (-2.30258509299), [X] -> 4 (-2.30258509299), [X] -> 5 (-2.30258509299)]
    """
    for line in istream:
        lhs, rhs, log_prob = line.strip().split(' ||| ')
        if not strip_quotes:
            rhs = rhs.split()
        else:
            rhs = [s[1:-1] if s.startswith("'") and s.endswith("'") else s for s in rhs.split()]
        log_prob = transform(float(log_prob))
        yield Rule(lhs, rhs, log_prob)

