__author__ = 'Iason'

from topSort import get_bs
from symbol import parse_annotated_nonterminal
import math
from scipy.stats import beta


class SlicedInside(object):

    def __init__(self, forest, sorted_forest, slice_variables, goal, a=0.1, b=1):
        self.forest = forest
        self.sorted_forest = sorted_forest
        self.slice_variables = slice_variables
        self.goal = goal
        self.a = a
        self.b = b

    """
    The actual algorithm
    """
    def inside(self):
        forest = self.forest
        sorted_forest = self.sorted_forest
        inside_prob = dict()

        # visit nodes bottom up
        for q in sorted_forest:
            incoming = get_bs(q, forest)

            # leaves have inside weight 1
            if len(incoming) < 1:
                # log(1) = 0
                inside_prob[q] = 0
            else:
                # log(0) = -inf
                inside_prob[q] = -float("inf")

                # total inside weight of an incoming edge
                for bs in incoming:
                    # replaced "k = bs.log_prob" for:
                    if not q == self.goal:
                        """ Question 3: is this the correct beta.pdf function? """
                        u = self.slice_variables[parse_annotated_nonterminal(bs.lhs)]
                        k = math.log(1 / beta.pdf(math.exp(u), self.a, self.b))

                    for e in bs.rhs:
                        # including the edge own weight
                        # log(a * b) = log(a) + log(b)
                        k = k + inside_prob[e]

                    # log(a) + log(b) = log(exp(a) + exp(b))
                    inside_prob[q] = math.log(math.exp(inside_prob[q]) + math.exp(k))

        return inside_prob

