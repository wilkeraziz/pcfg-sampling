__author__ = 'Iason'

from topSort import get_bs
from symbol import is_nonterminal
import math
import random


class GeneralisedSampling(object):

    def __init__(self, forest, inside_prob):
        self.forest = forest
        self.inside_prob = inside_prob

    """
    the generalised sample algorithm
    """
    def sample(self):
        # print "\n\n============= SAMPLING ==============="
        forest = self.forest
        inside_prob = self.inside_prob

        # an empty partial derivation
        d = []

        # Q, a queue of nodes to be visited, starting from [GOAL]
        q = ['[GOAL]']

        while q:
            k = q.pop()
            # print "\n============", k, "============"

            # select an edge
            e = select(k, inside_prob, forest)

            # print "\n\n====== selected edge = ", e

            # add the edge to the partial derivation
            d.append(e)

            # queue the non-terminal nodes in the tail of the selected edge
            for n in e.rhs:
                if is_nonterminal(n):
                    q.append(n)

        return d


"""
select method, draws a random edge with respect to the Inside weight distribution
"""
def select(k, inside, forest):
    iq = dict()
    k_bs = get_bs(k, forest)

    # the inside weight of the parent node
    ip = inside[k]

    # calculate the Inside weight for each edge in BS of parent node
    for b in k_bs:
        # edge own weight
        temp_iq = b.log_prob

        # consider all of its tail nodes
        for r in b.rhs:
            temp_iq = temp_iq + inside[r]

        iq[b] = temp_iq

    """
    print "\n All Iq: "
    for i, j in iq.iteritems():
        print i, "Iq --> ", j
    """

    # print "\nNormalisation term = ", ip

    # select an edge randomly with respect to the distribution of the edges
    # threshold for selecting an edge
    threshold = math.log(random.uniform(0, math.exp(ip)))

    acc = -float("inf")

    for e in k_bs:
        acc = math.log(math.exp(acc) + math.exp(iq[e]))

        """
        print "Thres =", threshold
        print "Iq e: ", iq[e], "iq = ", iq[e]
        print "cur edge = ", e
        print "acc = ", acc
        """

        if acc > threshold:
            return e

    # if there is not yet an edge returned for some rare rounding error,
    # return the last edge, hence that is the edge closest to the threshold
    return k_bs[-1]


