"""
@author wilkeraziz
"""

from collections import defaultdict

class Rule(object):

    def __init__(self, lhs, rhs, log_prob):
        """
        Constructs a Rule.
        @param lhs: the LHS nonterminal
        @param rhs: a sequence of RHS symbols
        @param log_prob: log probability of the rule 
        """
        self.lhs_ = lhs
        self.rhs_ = tuple(rhs)
        self.log_prob_ = log_prob

    def __eq__(self, other):
        return self.lhs_ == other.lhs_ and self.rhs_ == other.rhs_ and self.log_prob_ == other.log_prob_

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.lhs_, self.rhs_, self.log_prob_))

    def __repr__(self):
        return '%s -> %s (%s)' % (self.lhs_,
                ' '.join(str(sym) for sym in self.rhs_),
                self.log_prob_)

    @property
    def lhs(self):
        return self.lhs_

    @property
    def rhs(self):
        return self.rhs_
    
    @property
    def log_prob(self):
        return self.log_prob_

    @property
    def prob(self):
        return Math.exp(self.log_prob_)

