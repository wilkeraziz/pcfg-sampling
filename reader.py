"""

:Authors: Wilker Aziz
"""

import wcfg
import discodopfmt
from utils import smart_open
import math

def load_grammar(path, grammarfmt, transform):
    """
    Load a WCFG from a file.

    :args path: path to the grammar (or prefix path to rules and lexicon)
    :args grammarfmt: 'bar' or 'discodop'
    :returns: WCFG
    """
    if grammarfmt == 'bar':
        istream = smart_open(path)
        grammar = wcfg.WCFG(wcfg.read_grammar_rules(istream, transform))
    elif grammarfmt == 'discodop':
        grammar = discodopfmt.read_grammar('{0}.rules.gz'.format(path), '{0}.lex.gz'.format(path), transform)
    else:
        raise NotImplementedError("I don't know this grammar format: %s" % grammarfmt)
    return grammar
