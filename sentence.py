"""
:Authors: - Wilker Aziz
"""

import unknownmodel
from rule import Rule
from wfsa import WDFSA
import logging
from symbol import make_nonterminal, make_terminal

PASSTHROUGH = 'passthrough'
STFDBASE = 'stfdbase'
STFD4 = 'stfd4'
STFD6 = 'stfd6'
DEFAULT_SYMBOL = 'X'

class Sentence(object):

    def __init__(self, words, signatures, fsa):
        self._words = tuple(words)
        self._signatures = tuple(signatures)
        self._fsa = fsa

    def __len__(self):
        return len(self._words)

    @property
    def words(self):
        return self._words

    @property
    def signatures(self):
        return self._signatures

    @property
    def fsa(self):
        return self._fsa

    def __str__(self):
        return ' '.join(self.words)


def make_sentence(input_str, lexicon, unkmodel=None, default_symbol=DEFAULT_SYMBOL, one=0.0, split_bars=False):
    if split_bars:
        words = input_str.split(' ||| ')[0].split()  # this gets rid of whatever follows the triple bars
    else:
        words = input_str.split()
    signatures = list(words)
    extra_rules = []
    for i, word in enumerate(words):
        terminal = make_terminal(word)
        if terminal not in lexicon and unkmodel is not None:
            # special treatment for unknown words
                if unkmodel == PASSTHROUGH:
                    extra_rules.append(Rule(make_nonterminal(default_symbol), [terminal], one))
                    logging.debug('Passthrough rule for %s: %s', word, extra_rules[-1])
                else:
                    if unkmodel == STFDBASE:
                        get_signature = unknownmodel.unknownwordbase
                    elif unkmodel == STFD4:
                        get_signature = unknownmodel.unknownword4
                    elif unkmodel == STFD6:
                        get_signature = unknownmodel.unknownword6
                    else:
                        raise NotImplementedError('I do not know this model: %s' % unkmodel)
                    signatures[i] = get_signature(word, i, lexicon)
                    logging.debug('Unknown word model (%s): i=%d word=%s signature=%s', unkmodel, i, word, signatures[i])

    fsa = WDFSA()
    for i, word in enumerate(signatures):
        fsa.add_arc(i, i + 1, make_terminal(word), one)
    fsa.make_initial(0)
    fsa.make_final(len(signatures))
    return Sentence(words, signatures, fsa), extra_rules