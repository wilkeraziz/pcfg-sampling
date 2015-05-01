"""
@author wilkeraziz
"""

from collections import defaultdict

class WDFSA(object):
    """This is a deterministic wFSA"""

    def __init__(self):
        self._arcs = defaultdict(None)
        self._initial_states = set()
        self._final_states = set()

    def add_arc(self, sfrom, sto, symbol, log_prob=0.0):
        self._arcs[(sfrom, symbol)]  = (sto, log_prob)

    def make_initial(self, state):
        self._initial_states.add(state)

    def make_final(self, state):
        self._final_states.add(state)

    def destination_and_weight(self, sfrom, symbol):
        return self._arcs.get((sfrom, symbol), (None, None))
        
    @property
    def initial_states(self):
        return self._initial_states
    
    @property
    def final_states(self):
        return self._final_states

    def __str__(self):
        lines = []
        for (sfrom, symbol), (sto, log_prob) in self._arcs.iteritems():
            lines.append('(%d, %s, %d, %s)' % (sfrom, symbol, sto, log_prob))
        return '\n'.join(lines)
