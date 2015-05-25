__author__ = 'Iason'

import numpy
import math


class SliceVariable(object):

    def __init__(self, item, slice_variables, conditions, a=0.1, b=1):
        self.item = item
        self.slice_variables = slice_variables
        self.conditions = conditions
        self.a = a
        self.b = b

    """
    Returns a slice variable if it exists, otherwise calculates one based on the condition of the
    previous derivations or if none, on a beta distribution
    """
    def get(self):
        item = self.item
        state = item.rule.lhs, str(item.start), str(item.dot)
        slice_variables = self.slice_variables

        u = self.get_existing_slice_variable(state, slice_variables)

        if u is not None:
            return u
        else:
            theta = self.get_condition(state)

            if theta is None:
                slice_variables[state] = math.log(numpy.random.beta(self.a, self.b))
                return slice_variables[state]
            else:
                slice_variables[state] = math.log(numpy.random.uniform(0, math.exp(theta)))
                return slice_variables[state]

    """
    Get a slice variable for a given state if it exists
    """
    def get_existing_slice_variable(self, state, slice_variables):
        u = slice_variables.get(state)

        if u is not None:
            return u
        else:
            return None

    """
    Get the condition of a given state if it exists
    """
    def get_condition(self, state):
        if self.conditions.__contains__(state):
            return self.conditions[state]
        else:
            return None