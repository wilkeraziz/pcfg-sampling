"""
:Authors: - Wilker Aziz
"""

import itertools
from collections import deque, defaultdict
from symbol import make_symbol, is_nonterminal
from rule import Rule
from wcfg import WCFG


EMPTY_SET = frozenset()


class ActiveQueue(object):
    """
    Implement a queue of active items.
    However the queue guarantee that an item never queues more than once.
    """

    def __init__(self):
        self._active = deque()  # items to be processed
        self._seen = set()  # items that are queuing (or have already left the queue)

    def __len__(self):
        """Number of active items queuing to be processed"""
        return len(self._active)

    def pop(self):
        """Returns the next active item"""
        return self._active.popleft()

    def add(self, item):
        """Add an active item if possible"""
        if item not in self._seen:
            self._active.appendleft(item)
            self._seen.add(item)
            return True
        return False


class Agenda(object):
    """
    This is a CKY agenda which implements the algorithm by Nederhof and Satta (2008).
    It consists of:
        1) a queue of active items
        2) a set of generating intersected nonterminals
        3) a set of passive items
        4) a set of complete items
    """

    def __init__(self, active_container_type=ActiveQueue):
        self._active_container_type = active_container_type
        self._active = active_container_type()  # items to be processed
        self._passive = defaultdict(set)  # passive items waiting for completion: (LHS, start) -> items
        self._generating = defaultdict(lambda: defaultdict(set))  # generating symbols: LHS -> start -> ends
        self._complete = defaultdict(set)  # complete items

    def __len__(self):
        """Number of active items queuing to be processed"""
        return len(self._active)

    def pop(self):
        """Returns the next active item"""
        return self._active.pop()

    def add(self, item):
        """Add an active item if possible"""
        return self._active.add(item)

    def extend(self, items):
        for item in items:
            self.add(item)

    def is_passive(self, item):
        """Whether or not an item is passive"""
        return item in self._passive.get((item.next, item.dot), set())

    def add_generating(self, sym, sfrom, sto):
        """
        Tries to add a newly discovered generating symbol.
        Returns False if the symbol already exists, True otherwise.
        """
        destinations = self._generating[sym][sfrom]
        n = len(destinations)
        destinations.add(sto)
        return len(destinations) > n

    def is_generating(self, sym, sfrom, sto):
        return sto in self._generating.get(sym, {}).get(sfrom, set())

    def make_passive(self, item):
        """
        Tries to make passive an active item.
        Returns False if the item is already passive, True otherwise.
        """
        waiting = self._passive[(item.next, item.dot)]
        n = len(waiting)
        waiting.add(item)
        return len(waiting) > n

    def make_complete(self, item):
        """Stores a complete item"""
        self._complete[(item.rule.lhs, item.start, item.dot)].add(item)
        self.add_generating(item.rule.lhs, item.start, item.dot)

    def discard(self, item):
        waiting = self._passive.get((item.next, item.dot), None)
        if waiting:
            try:
                waiting.remove(item)
            except KeyError:
                pass

    def itergenerating(self, sym):
        """Returns an iterator to pairs of the kind (start, set of ends) for generating items based on a given symbol"""
        return self._generating.get(sym, {}).iteritems()

    def itercomplete(self, lhs=None, start=None, end=None):
        """
        Iterates through complete items whose left hand-side is (start, lhs, end)
        or through all of them if lhs is None
        """
        return itertools.chain(*self._complete.itervalues()) if lhs is None else iter(self._complete.get((lhs, start, end), set()))

    def iterwaiting(self, sym, start):
        """Returns items waiting for a certain symbol to complete from a certain state"""
        return iter(self._passive.get((sym, start), frozenset()))

    def itercompletions(self, sym, start):
        """Return possible completions of the given item"""
        return iter(self._generating.get(sym, {}).get(start, frozenset()))


def get_intersected_rule(item):
    lhs = make_symbol(item.rule.lhs, item.start, item.dot)
    positions = item.inner + (item.dot,)
    rhs = [make_symbol(sym, positions[i], positions[i + 1]) for i, sym in enumerate(item.rule.rhs)]
    return Rule(lhs, rhs, item.rule.log_prob)


def get_cfg(goal, root, fsa, agenda):
    """
    Constructs the CFG by visiting complete items in a top-down fashion.
    This is effectively a reachability test and it serves the purpose of filtering nonterminal symbols
    that could never be reached from the root.
    Note that bottom-up intersection typically does enumerate a lot of useless (unreachable) items.
    This is the recursive procedure described in the paper (Nederhof and Satta, 2008).
    """

    G = WCFG()
    processed = set()

    def make_rules(lhs, start, end):
        if (start, lhs, end) in processed:
            return
        processed.add((lhs, start, end))
        for item in agenda.itercomplete(lhs, start, end):
            G.add(get_intersected_rule(item))
            fsa_states = item.inner + (item.dot,)
            for i, sym in itertools.ifilter(lambda (_, s): is_nonterminal(s), enumerate(item.rule.rhs)):
                if (sym, fsa_states[i], fsa_states[
                        i + 1]) not in processed:  # Nederhof does not perform this test, but in python it turned out crucial
                    make_rules(sym, fsa_states[i], fsa_states[i + 1])

    # create goal items
    for start, ends in agenda.itergenerating(root):
        if not fsa.is_initial(start):
            continue
        for end in itertools.ifilter(lambda q: fsa.is_final(q), ends):
            make_rules(root, start, end)
            G.add(Rule(make_symbol(goal, None, None),
                       [make_symbol(root, start, end)], 0.0))

    return G
