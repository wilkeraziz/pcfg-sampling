"""
@author wilkeraziz
"""

from collections import defaultdict
from symbol import is_terminal


class WCFG(object):

    def __init__(self):
        self._rules = []
        self._rule_by_lhs = defaultdict(list)

    def add_rule(self, rule):
        self._rules.append(rule)
        self._rules_by_lhs[rule.lhs].append(rule)

    def __getitem__(self, lhs):
        return self._rules_by_lhs.get(lhs, frozenset())

    def __iter__(self):
        return iter(self._rules)
    
    def iteritems(self):
        return self._rules_by_lhs.iteritems()

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
