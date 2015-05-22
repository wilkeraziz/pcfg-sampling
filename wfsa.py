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
        self._vocab = set()

    def itersymbols(self):
        return iter(self._vocab)

    def add_arc(self, sfrom, sto, symbol, log_prob=0.0):
        self._arcs[(sfrom, symbol)]  = (sto, log_prob)
        self._vocab.add(symbol)

    def make_initial(self, state):
        self._initial_states.add(state)

    def make_final(self, state):
        self._final_states.add(state)

    def destination_and_weight(self, sfrom, symbol):
        return self._arcs.get((sfrom, symbol), (None, None))
        
    @property
    def initial_states(self):
        return self._initial_states

    def is_initial(self, state):
        return state in self._initial_states

    def is_final(self, state):
        return state in self._final_states
    
    @property
    def final_states(self):
        return self._final_states

    def __str__(self):
        lines = []
        for (sfrom, symbol), (sto, log_prob) in self._arcs.iteritems():
            lines.append('(%d, %s, %d, %s)' % (sfrom, symbol, sto, log_prob))
        return '\n'.join(lines)

def make_linear_fsa(input_str):
    wfsa = WDFSA()
    tokens = input_str.split()
    for i, token in enumerate(tokens):
        wfsa.add_arc(i, i + 1, token)
    wfsa.make_initial(0)
    wfsa.make_final(len(tokens))
    return wfsa

