__author__ = 'Iason'

from topSort import get_bs
import math


class Inside(object):

    def __init__(self, forest, sorted_forest):
        self.forest = forest
        self.sorted_forest = sorted_forest

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
                    k = bs.log_prob

                    for e in bs.rhs:
                        # including the edge own weight
                        # log(a * b) = log(a) + log(b)
                        k = k + inside_prob[e]

                    # log(a) + log(b) = log(exp(a) + exp(b))
                    inside_prob[q] = math.log(math.exp(inside_prob[q]) + math.exp(k))

        return inside_prob

