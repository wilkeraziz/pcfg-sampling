"""
:Authors: - Iason
"""

from collections import defaultdict, deque


def top_sort(forest):
    """
    Partial ordering of nodes in the forest.
    :return: list of nodes ordered from leaves to root
    """

    dependencies = defaultdict(set)
    dependants = defaultdict(set)
    for lhs, rules in forest.iteritems():
        for rule in rules:
            dependencies[lhs].update(rule.rhs)
            for s in rule.rhs:
                dependants[s].add(lhs)

    sorting = deque(forest.terminals)

    # L, top ordered nodes
    ordered = []

    while sorting:
        # remove and return a node from sorting
        node = sorting.popleft()

        # append node to L
        ordered.append(node)

        parents = dependants.get(node, None)
        if parents:
            for parent in parents:
                deps = dependencies.get(parent, None)
                if deps is not None:
                    try:
                        deps.remove(node)
                    except KeyError:
                        pass
                    if len(deps) == 0:
                        sorting.append(parent)
                        del dependencies[parent]

    return ordered

