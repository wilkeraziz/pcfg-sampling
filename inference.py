"""
:Authors: - Iason
"""

from collections import defaultdict
import numpy as np


def inside(forest, topsort, omega=lambda edge: edge.log_prob):
    """
    Inside recursion.
    :param forest: an acyclic hypergraph.
    :param topsort: a partial ordering of the nodes in the forest.
    :param omega: a function that computes the weight of an edge (defaults to the edge's own log probability)
    :return: a dictionary mapping a symbol to its inside weight.
    """
    inside_prob = defaultdict(float)

    # visit nodes bottom up
    for parent in topsort:

        incoming = forest.get(parent, frozenset())

        # leaves have inside weight 1
        if not incoming:
            # log(1) = 0
            inside_prob[parent] = 0
        else:
            # log(0) = -inf
            total = -float("inf")

            for edge in incoming:
                w = sum((inside_prob[child] for child in edge.rhs), omega(edge))
                # log(a) + log(b) = log(exp(a) + exp(b))
                # total = log(exp(total) + exp(w))
                total = np.logaddexp(total, w)

            inside_prob[parent] = total

    return inside_prob

