"""
Read grammars encoded in bitpar/discodop's format.

:Authors: Wilker Aziz
"""

import sys
from itertools import chain
from rule import Rule
from wcfg import WCFG
from utils import smart_open
from symbol import make_nonterminal, make_terminal
import math


def iterrules(path, transform):
    fi = smart_open(path)
    for line in fi:
        line = line.strip()
        if not line:
            continue
        fields = line.split()
        lhs = fields[0]
        num, den = fields[-1].split('/')
        num = float(num)
        den = float(den)
        rhs = fields[1:-2]  # fields[-2] is the yield function, which we are ignoring
        yield Rule(make_nonterminal(lhs), [make_nonterminal(s) for s in rhs], transform(num/den))


def iterlexicon(path, transform):
    fi = smart_open(path)
    for line in fi:
        line = line.strip()
        if not line:
            continue
        fields = line.split('\t')
        word = fields[0]
        for pair in fields[1:]:
            tag, fraction = pair.split(' ')
            num, den = fraction.split('/')
            num = float(num)
            den = float(den)
            yield Rule(make_nonterminal(tag), [make_terminal(word)], transform(num/den))


def read_grammar(rules_file, lexicon_file, transform=math.log):
    return WCFG(chain(iterrules(rules_file, transform), iterlexicon(lexicon_file, transform)))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: %s rules lexicon' % (sys.argv[0])
        sys.exit(0)
    print read_grammar(sys.argv[1], sys.argv[2])
