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
    :args grammarfmt: 'bar',  'discodop' or 'milos' (which looks like 'bar' but with terminals surrounded by quotes)
    :returns: WCFG
    """
    if grammarfmt == 'bar':
        istream = smart_open(path)
        grammar = wcfg.WCFG(wcfg.read_grammar_rules(istream, transform))
    elif grammarfmt == 'milos':
        istream = smart_open(path)
        grammar = wcfg.WCFG(wcfg.read_grammar_rules(istream, transform, strip_quotes=True))
    elif grammarfmt == 'discodop':
        grammar = discodopfmt.read_grammar('{0}.rules.gz'.format(path), '{0}.lex.gz'.format(path), transform)
    else:
        raise NotImplementedError("I don't know this grammar format: %s" % grammarfmt)
    return grammar
