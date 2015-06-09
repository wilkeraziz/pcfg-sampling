"""
This is an implementation of the bottom-up intersection by Nederhof and Satta (2008) described in the paper:

    @inproceedings{Nederhof+2008:probparsing,
        Author = {Mark-Jan Nederhof and Giorgio Satta},
        Booktitle = {New Developments in Formal Languages and Applications, Studies in Computational Intelligence},
        Editor = {G. Bel-Enguix, M. Dolores Jim{\\'e}nez-L{\\'o}pez, and C. Mart{\\'\\i}n-Vide},
        Pages = {229-258},
        Publisher = {Springer},
        Title = {Probabilistic Parsing},
        Volume = {113},
        Year = {2008}
    }

:Authors: 
    - Wilker Aziz
    - Iason
"""

from collections import defaultdict, deque
from itertools import ifilter
from agenda import Agenda, ActiveQueue, get_cfg
from item import ItemFactory
from symbol import is_terminal, make_symbol, is_nonterminal
from rule import Rule
from wcfg import WCFG
import logging
from slice_variable import SliceVariable


class SlicedNederhof(object):
    """
    This is an implementation of the CKY-inspired intersection due to Nederhof and Satta (2008).
    """

    def __init__(self, wcfg, wfsa, slice_vars):
        self._wcfg = wcfg
        self._wfsa = wfsa
        self._agenda = Agenda(active_container_type=ActiveQueue)
        self._firstsym = defaultdict(set)  # index rules by their first RHS symbol
        self._item_factory = ItemFactory()
        self.slice_vars = slice_vars

    def get_item(self, rule, dot, inner=[]):
        return self._item_factory.get_item(rule, dot, inner)
    
    def advance(self, item, dot):
        """returns a new item whose dot has been advanced"""
        return self.get_item(item.rule, dot, item.inner + (item.dot,))
        
    def add_symbol(self, sym, sfrom, sto):
        """
        This operation:
            1) completes items waiting for `sym` from `sfrom`
            2) instantiate delayed axioms
        Returns False if the annotated symbol had already been added, True otherwise
        """
        
        if self._agenda.is_generating(sym, sfrom, sto):
            return False

        # every item waiting for `sym` from `sfrom`
        for item in self._agenda.iterwaiting(sym, sfrom):
            self._agenda.add(self.advance(item, sto))

        # you may interpret this as a delayed axiom
        # every compatible rule in the grammar
        for r in self._firstsym.get(sym, set()):  
            self._agenda.add(self.get_item(r, sto, inner=(sfrom,)))  # can be interpreted as a lazy axiom

        return True

    def axioms(self):
        """
        The axioms of the program are based on the FSA transitions. 
        """
        # you may interpret the following as a sort of lazy axiom (based on grammar rules)
        for r in self._wcfg:
            self._firstsym[r.rhs[0]].add(r)
        # these are axioms based on the transitions of the automaton
        for sfrom, sto, sym, w in self._wfsa.iterarcs():
            self.add_symbol(sym, sfrom, sto)  

    def inference(self):
        """Exhausts the queue of active items"""
        agenda = self._agenda
        while agenda:
            item = agenda.pop()  # always returns an ACTIVE item
            # complete other items (by calling add_symbol), in case the input item is complete
            if item.is_complete():
                u = self.slice_vars.get(item.rule.lhs, item.start, item.dot)
                # check whether the probability of the current completed item is above the threshold determined by
                # the slice variable
                if item.rule.log_prob > u:
                    self.add_symbol(item.rule.lhs, item.start, item.dot)  # prove the symbol
                    agenda.make_complete(item)  # mark the item as complete
            else:
                # merges the input item with previously completed items effectively moving the input item's dot forward
                agenda.make_passive(item)
                for sto in agenda.itercompletions(item.next, item.dot):
                    agenda.add(self.advance(item, sto))  # move the dot forward

    def do(self, root='[S]', goal='[GOAL]'):
        """Runs the program and returns the intersected CFG"""
        self.axioms()
        self.inference()
        return get_cfg(goal, root, self._wfsa, self._agenda)
