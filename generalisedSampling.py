__author__ = 'Iason'

from symbol import is_nonterminal
import math
import random


class GeneralisedSampling(object):

    def __init__(self, forest, inside_prob):
        self.forest = forest
        self.inside = inside_prob
        self.iq = dict()

    def sample(self, goal='[GOAL]'):
        """
        the generalised sample algorithm
        """

        # an empty partial derivation
        d = []

        # Q, a queue of nodes to be visited, starting from [GOAL]
        q = [goal]

        while q:
            k = q.pop()

            # select an edge
            e = self.select(k)

            # add the edge to the partial derivation
            d.append(e)

            # queue the non-terminal nodes in the tail of the selected edge
            for n in e.rhs:
                if is_nonterminal(n):
                    q.append(n)

        return d

    def select(self, k):
        """
        select method, draws a random edge with respect to the Inside weight distribution
        """
        # self.iq = dict()
        k_bs = self.forest.get(k, frozenset())

        # the inside weight of the parent node
        ip = self.inside[k]

        # calculate the Inside weight for each edge in BS of parent node
        for b in k_bs:
            if b not in self.iq:
                # edge own weight
                temp_iq = b.log_prob

                # consider all of its tail nodes
                for r in b.rhs:
                    temp_iq += self.inside[r]

                self.iq[b] = temp_iq

        # select an edge randomly with respect to the distribution of the edges
        # threshold for selecting an edge
        threshold = math.log(random.uniform(0, math.exp(ip)))

        acc = -float("inf")

        for e in k_bs:
            acc = math.log(math.exp(acc) + math.exp(self.iq[e]))

            if acc > threshold:
                return e

        # if there is not yet an edge returned for some rare rounding error,
        # return the last edge, hence that is the edge closest to the threshold
        return k_bs[-1]


