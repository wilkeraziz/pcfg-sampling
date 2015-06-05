__author__ = 'Iason'

import math
from collections import defaultdict


def inside(forest, topsort):
    """
    Inside recursion.
    :return: a dictionary mapping a symbol to its inside weight.
    """
    inside_prob = defaultdict(float)

    # visit nodes bottom up
    for parent in topsort:

        rules = forest.get(parent, frozenset())

        # leaves have inside weight 1
        if not rules:
            # log(1) = 0
            inside_prob[parent] = 0
        else:
            # log(0) = -inf
            total = -float("inf")

            for rule in rules:
                k = rule.log_prob

                for child in rule.rhs:
                    # including the rule own weight
                    # log(a * b) = log(a) + log(b)
                    k += inside_prob[child]

                # log(a) + log(b) = log(exp(a) + exp(b))
                total = math.log(math.exp(total) + math.exp(k))

            inside_prob[parent] = total

    return inside_prob

