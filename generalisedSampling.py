"""
:Authors: - Iason
"""

from symbol import is_nonterminal
import random
import numpy as np


class GeneralisedSampling(object):

    def __init__(self, forest, inside_node, omega=lambda edge: edge.log_prob):
        """

        :param forest: an acyclic hypergraph
        :param inside_node: a dictionary mapping nodes to their inside weights.
        :param omega: a function that returns the weight of an edge.
            By default we return the edge's log probability, but omega
            can be used in situations where we must compute a function of that weight, for example,
            when we want to convert from a semiring to another,
            or when we want to compute a uniform probability based on assingments of the slice variables.
        """

        self.forest = forest
        self.inside_node = inside_node
        self.inside_edge = dict()  # cache for the inside weight of edges
        self.omega = omega

    def sample(self, goal='[GOAL]'):
        """
        the generalised sample algorithm
        """

        # an empty partial derivation
        d = []

        # Q, a queue of nodes to be visited, starting from [GOAL]
        Q = [goal]

        while Q:
            parent = Q.pop()

            # select an edge
            edge = self.select(parent)

            # add the edge to the partial derivation
            d.append(edge)

            # queue the non-terminal nodes in the tail of the selected edge
            for child in edge.rhs:
                if is_nonterminal(child):
                    Q.append(child)

        return d

    def get_edge_inside(self, edge):
        """Compute the inside weight of an edge (caching the result)."""
        w = self.inside_edge.get(edge, None)
        if w is None:
            # starting from the edge's own weight
            # and including the inside of each child node
            # accumulate (log-domain) all contributions
            w = sum((self.inside_node[child] for child in edge.rhs), self.omega(edge))
            self.inside_edge[edge] = w
        return w

    def select(self, parent):
        """
        select method, draws a random edge with respect to the Inside weight distribution
        """
        # self.iq = dict()
        incoming = self.forest.get(parent, frozenset())

        if not incoming:
            raise ValueError('I cannot sample an incoming edge to a terminal node')

        # the inside weight of the parent node
        ip = self.inside_node[parent]

        # select an edge randomly with respect to the distribution of the edges
        # threshold for selecting an edge
        threshold = np.log(random.uniform(0, np.exp(ip)))

        acc = -float("inf")
        for e in incoming:
            # acc = math.log(math.exp(acc) + math.exp(self.get_edge_inside(e)))
            acc = np.logaddexp(acc, self.get_edge_inside(e))
            if acc > threshold:
                return e

        # if there is not yet an edge returned for some rare rounding error,
        # return the last edge, hence that is the edge closest to the threshold
        return e


