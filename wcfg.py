"""
@author wilkeraziz
"""

from collections import defaultdict, deque
from symbol import is_terminal


class WCFG(object):

    def __init__(self):
        self._rules = []
        self._rules_by_lhs = defaultdict(list)

    def add_rule(self, rule):
        self._rules.append(rule)
        self._rules_by_lhs[rule.lhs].append(rule)

    def __getitem__(self, lhs):
        return self._rules_by_lhs.get(lhs, frozenset())

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

class FrozenWCFG(object):

    def __init__(self, rules):
        self._rules = tuple(rules)
        helper = defaultdict(list)
        [helper[rule.lhs].append(rule) for rule in self._rules]
        self._rules_by_lhs = defaultdict(None)
        for lhs, entries in helper.iteritems():
            self._rules_by_lhs[lhs] = frozenset(entries)

    def __getitem__(self, lhs):
        return self._rules_by_lhs.get(lhs, frozenset())

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
    counts = {'d': defaultdict(int), 'p': defaultdict(int)}
    recursion([], [], deque([root]), wcfg, counts)
    return counts

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
