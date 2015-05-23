"""
@author wilkeraziz
"""

import logging
import itertools
import argparse
import sys
from rule import Rule
from symbol import is_nonterminal, is_terminal
from wcfg import WCFG, count_derivations
from wfsa import WDFSA, make_linear_fsa
from earley import Earley

def make_grammar(fsa):
    cfg = WCFG()
    cfg.add(Rule('[S]', ['[X]'], 0.0))
    cfg.add(Rule('[X]', ['[X]', '[X]'], 0.0))
    for word in fsa.itersymbols():
        cfg.add(Rule('[X]', [word], 0.0))
    return cfg

def main(args):

    for input_str in args.input:
        fsa = make_linear_fsa(input_str)
        cfg = make_grammar(fsa)
        parser = Earley(cfg, fsa)
        forest = parser.do('[S]', '[GOAL]')
        if not forest:
            print 'NO PARSE FOUND'
            continue
        new_rules = []
        for rule in forest:
            if len(rule.rhs) > 1 and all(map(is_nonterminal, rule.rhs)):
                new_rules.append(Rule(rule.lhs, reversed(rule.rhs), rule.log_prob))
        [forest.add(rule) for rule in new_rules]
        print '# FOREST'
        print forest
        print

        if args.show_permutations:
            counts = count_derivations(forest, '[GOAL]')
            total = 0
            for p, n in sorted(counts['p'].iteritems(), key=lambda (k, v): k):
                print p, n
                total += n
            print len(counts['p'].keys()), total



def argparser():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(prog='parse')

    parser.description = 'Binarizable permutations'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus (one sentence per line)')
    #parser.add_argument('output', nargs='?', 
    #        type=argparse.FileType('w'), default=sys.stdout,
    #        help='parse trees')
    parser.add_argument('--show-permutations', 
            action='store_true',
            help='enumerate permutations (use with care)')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
