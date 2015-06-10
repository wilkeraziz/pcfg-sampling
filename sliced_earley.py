"""
This work is based on the work of wilkeraziz: earley.py
And extended with Slice Sampling by Iason

:Authors: 
    - Wilker Aziz
    - Iason
"""

EMPTY_SET = frozenset()
import logging
from agenda import Agenda, ActiveQueue
from item import ItemFactory
from symbol import is_terminal, make_symbol, is_nonterminal
from rule import Rule
from wcfg import WCFG
import itertools
from slice_variable import SliceVariable


class SlicedEarley(object):
    """
    """

    def __init__(self, wcfg, wfsa, slice_vars):
        """
        """

        self._wcfg = wcfg
        self._wfsa = wfsa
        self._agenda = Agenda(active_container_type=ActiveQueue)
        self._predictions = set()  # (LHS, start)
        self._item_factory = ItemFactory()
        self.slice_vars = slice_vars

    def get_item(self, rule, dot, inner=[]):
        return self._item_factory.get_item(rule, dot, inner)

    def advance(self, item, dot):
        """returns a new item whose dot has been advanced"""
        return self.get_item(item.rule, dot, item.inner + (item.dot,))

    def axioms(self, symbol, start):
        rules = self._wcfg.get(symbol, None)
        if rules is None:  # impossible to rewrite the symbol
            return False
        if (symbol, start) in self._predictions:  # already predicted
            return True
        # otherwise add rewritings to the agenda
        self._predictions.add((symbol, start))
        self._agenda.extend(self.get_item(rule, start) for rule in rules)
        return True

    def prediction(self, item):
        """
        This operation tris to create items from the rules associated with the nonterminal ahead of the dot.
        It returns True when prediction happens, and False if it already happened before.
        """
        if (item.next, item.dot) in self._predictions:  # prediction already happened
            return False
        self._predictions.add((item.next, item.dot))
        new_items = [self.get_item(rule, item.dot) for rule in self._wcfg.get(item.next, frozenset())]
        self._agenda.extend(new_items)
        return True

    def scan(self, item):
        """
        This operation tries to scan over as many terminals as possible,
        but we only go as far as determinism allows.
        If we get to a nondeterminism, we stop scanning and add the relevant items to the agenda.
        """
        states = [item.dot]
        for sym in item.nextsymbols():
            if is_terminal(sym):
                arcs = self._wfsa.get_arcs(origin=states[-1], symbol=sym)
                if len(arcs) == 0:  # cannot scan the symbol
                    return False
                elif len(arcs) == 1:  # symbol is scanned deterministically
                    sto, _ = arcs[0]
                    states.append(sto)  # we do not create intermediate items, instead we scan as much as we can
                else:  # here we found a nondeterminism, we create all relevant items and add them to the agenda
                    # create items
                    for sto, w in arcs:
                        self._agenda.add(self.get_item(item.rule, sto, item.inner + tuple(states)))
                    return True
            else:  # that's it, scan bumped into a nonterminal symbol, time to wrap up
                break
        # here we should have scanned at least one terminal symbol
        # and we defined a deterministic path
        self._agenda.add(self.get_item(item.rule, states[-1], item.inner + tuple(states[:-1])))
        return True

    def complete_others(self, item):
        """
        This operation creates new item by advancing the dot of passive items that are waiting for a certain given complete item.
        It returns whether or not at least one passive item awaited for the given complete item.
        """
        if self._agenda.is_generating(item.rule.lhs, item.start, item.dot):
            return True
        new_items = [self.advance(incomplete, item.dot) for incomplete in self._agenda.iterwaiting(item.rule.lhs, item.start)]
        self._agenda.extend(new_items)
        return len(new_items) > 0  # was there any item waiting for the complete one?


    def complete_itself(self, item):
        """
        This operation tries to merge a given incomplete item with a previosly completed one.
        """
        new_items = [self.advance(item, sto) for sto in self._agenda.itercompletions(item.next, item.dot)]
        self._agenda.extend(new_items)
        return len(new_items) > 0

    def do(self, root='[S]', goal='[GOAL]'):

        wfsa = self._wfsa
        wcfg = self._wcfg
        agenda = self._agenda

        # start items of the kind
        # GOAL -> * ROOT, where * is an intial state of the wfsa
        if not any(self.axioms(root, start) for start in wfsa.iterinitial()):
            raise ValueError('No rule for the start symbol %s' % root)
        new_roots = set()

        while agenda:
            item = agenda.pop()  # always returns an active item

            if item.is_complete():
                # get slice variable for the current completed item
                u = self.slice_vars.get(item.rule.lhs, item.start, item.dot)

                # check whether the probability of the current completed item is above the threshold determined by
                # the slice variable
                if item.rule.log_prob > u:
                    # complete root item spanning from a start wfsa state to a final wfsa state
                    if item.rule.lhs == root and wfsa.is_initial(item.start) and wfsa.is_final(item.dot):
                        agenda.make_complete(item)
                        new_roots.add((root, item.start, item.dot))
                        agenda.make_passive(item)
                    else:
                        if self.complete_others(item):
                            agenda.make_complete(item)
                            agenda.make_passive(item)
                        else:  # a complete state is only kept in case it could potentially complete others
                            agenda.discard(item)
            else:
                if is_terminal(item.next):
                    # fire the operation 'scan'
                    self.scan(item)
                    agenda.discard(item)  # scanning renders incomplete items of this kind useless
                else:
                    if not wcfg.can_rewrite(item.next):  # if the NT does not exist this item is useless
                        agenda.discard(item)
                    else:
                        if not self.prediction(item):  # try to predict, otherwise try to complete itself
                            self.complete_itself(item)
                        agenda.make_passive(item)
        # converts complete items into rules
        logging.debug('Making forest...')
        return self.get_cfg(goal, root)

    def get_intersected_rule(self, item):
        lhs = make_symbol(item.rule.lhs, item.start, item.dot)
        positions = item.inner + (item.dot,)
        rhs = [make_symbol(sym, positions[i], positions[i + 1]) for i, sym in enumerate(item.rule.rhs)]
        return Rule(lhs, rhs, item.rule.log_prob)

    def get_cfg(self, goal, root):
        """
        Constructs the CFG by visiting complete items in a top-down fashion.
        This is effectively a reachability test and it serves the purpose of filtering nonterminal symbols
        that could never be reached from the root.
        Note that bottom-up intersection typically does enumerate a lot of useless (unreachable) items.
        This is the recursive procedure described in the paper (Nederhof and Satta, 2008).
        """

        G = WCFG()
        processed = set()
        fsa = self._wfsa
        itergenerating = self._agenda.itergenerating
        itercomplete = self._agenda.itercomplete

        def make_rules(lhs, start, end):
            if (start, lhs, end) in processed:
                return
            processed.add((lhs, start, end))
            for item in itercomplete(lhs, start, end):
                G.add(self.get_intersected_rule(item))
                fsa_states = item.inner + (item.dot,)
                for i, sym in itertools.ifilter(lambda (_, s): is_nonterminal(s), enumerate(item.rule.rhs)):
                    if (sym, fsa_states[i], fsa_states[
                            i + 1]) not in processed:  # Nederhof does not perform this test, but in python it turned out crucial
                        make_rules(sym, fsa_states[i], fsa_states[i + 1])

        # create goal items
        for start, ends in itergenerating(root):
            if not fsa.is_initial(start):
                continue
            for end in itertools.ifilter(lambda q: fsa.is_final(q), ends):
                make_rules(root, start, end)
                G.add(Rule(make_symbol(goal, None, None),
                           [make_symbol(root, start, end)], 0.0))

        return G
