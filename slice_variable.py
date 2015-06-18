"""
:Authors: - Iason
"""

import numpy
import math
from scipy.stats import beta
from collections import defaultdict
import logging


class SliceVariable(object):

    def __init__(self, slice_variables={}, conditions={}, a=0.1, b=1):
        self.slice_variables = defaultdict(None, slice_variables)
        self.conditions = defaultdict(None, conditions)
        self.a = a
        self.b = b

    def get(self, sym, start, end):
        """
        Returns a slice variable if it exists, otherwise calculates one based on the condition of the
        previous derivations or if none, on a beta distribution
        """
        # slice variables are indexed by the annotated LHS symbol as shown below
        state = (sym, start, end)
        # try to retrieve an assignment of the slice variable
        u = self.slice_variables.get(state, None)
        if u is None:  # if we have never computed such an assignment
            theta = self.conditions.get(state, None)  # first we try to retrieve a condition
            if theta is None:  # if there is none
                u = math.log(numpy.random.beta(self.a, self.b))  # the option is to sample u from a beta
            else:  # otherwise
                u = math.log(numpy.random.uniform(0, math.exp(theta)))  # we must sample u uniformly in the interval [0, theta)
            self.slice_variables[state] = u  # finally we store u for next time
        return u

    def reset(self, conditions=None, a=None, b=None):
        """
        
        """
        self.slice_variables = defaultdict(None)  # the actual slice variables always get reset
        if conditions is not None:  # we overwrite conditions only if necessary
            self.conditions = defaultdict(None, conditions)
        # similarly for the parameters
        if a is not None:
            self.a = a
        if b is not None:
            self.b = b

    def weight(self, sym, start, end, theta):
        state = (sym, start, end)
        try:
            u = self.slice_variables[state]
        except:
            raise ValueError('I do not expect to reweight a rule for an unseen state: %s' % str(state))

        if theta > u:
            return - beta.logpdf(math.exp(u), self.a, self.b)

        else:
            raise ValueError('I do not expect to reweight rules scoring less than the threshold')


