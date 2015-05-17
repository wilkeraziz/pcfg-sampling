"""
@author wilkeraziz
"""

import logging
import itertools
import argparse
import sys
from rule import Rule
from symbol import is_nonterminal, is_terminal
from wcfg import FrozenWCFG, WCFG, count_derivations
from wfsa import WDFSA
from earley import Earley

def read_grammar_rules(istream):
    for line in istream:
        lhs, rhs, log_prob = line.strip().split(' ||| ')
        rhs = rhs.split()
        log_prob = float(log_prob)
        yield Rule(lhs, rhs, log_prob)

def make_linear_fsa(input_str):
    wfsa = WDFSA()
    tokens = input_str.split()
    for i, token in enumerate(tokens):
        wfsa.add_arc(i, i + 1, token)
    wfsa.make_initial(0)
    wfsa.make_final(len(tokens))
    return wfsa

def main(args):
    wcfg = WCFG(read_grammar_rules(args.grammar))
    #print 'GRAMMAR'
    #print wcfg

    for input_str in args.input:
        wfsa = make_linear_fsa(input_str)
        #print 'FSA'
        #print wfsa
        parser = Earley(wcfg, wfsa)
        status, R = parser.do('[S]', '[GOAL]')
        if not status:
            print 'NO PARSE FOUND'
            continue
        forest = WCFG()
        for rule in R:
            forest.add_rule(rule)
            #continue
            if len(rule.rhs) > 1 and all(map(is_nonterminal, rule.rhs)):
                forest.add_rule(Rule(rule.lhs, reversed(rule.rhs), rule.log_prob))
        print '# FOREST'
        print forest
        print

        if args.show_permutations:
            print '# PERMUTATIONS'
            counts = count_derivations(forest, '[GOAL]')
            total = 0
            for p, n in sorted(counts['p'].iteritems(), key=lambda (k, v): k):
                print 'permutation=(%s) derivations=%d' % (' '.join(str(i) for i in p), n)
                total += n
            print 'permutations=%d derivations=%d' % (len(counts['p'].keys()), total)
            print



def argparser():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(prog='parse')

    parser.description = 'Earley parser'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('grammar',  
            type=argparse.FileType('r'), 
            help='CFG rules')
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus (one sentence per line)')
    parser.add_argument('--show-permutations',
            action='store_true',
            help='dumps all permutations (use with caution)')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
