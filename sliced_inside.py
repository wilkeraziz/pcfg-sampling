__author__ = 'Iason'

import math
from collections import defaultdict
from scipy.stats import beta
from symbol import parse_annotated_nonterminal
import logging


def sliced_inside(forest, topsort, goal, slice_variables):
    """
    Sliced Inside recursion.
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
              
                # weight of the rule
                if not parent == goal:  # rules rooted by the goal symbol have probability 1 (or 0 in log-domain) and there is no slice variable for the goal symbol
                    sym, start, end = parse_annotated_nonterminal(rule.lhs)
                    k = slice_variables.weight(sym, start, end, rule.log_prob)

                # inside of children
                for child in rule.rhs:
                    # including the rule own weight
                    # log(a * b) = log(a) + log(b)
                    k += inside_prob[child]

                # log(a) + log(b) = log(exp(a) + exp(b))
                total = math.log(math.exp(total) + math.exp(k))

            inside_prob[parent] = total

    return inside_prob

