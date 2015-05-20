"""
@author wilkeraziz
"""

import argparse
import sys

from rule import Rule
from wcfg import FrozenWCFG
from wfsa import WDFSA
from earley import Earley
from topSort import TopSort
from inside import Inside
from generalisedSampling import GeneralisedSampling


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
    wcfg = FrozenWCFG(read_grammar_rules(args.grammar))

    # print 'GRAMMAR'
    # print wcfg

    for input_str in args.input:
        wfsa = make_linear_fsa(input_str)
        # print 'FSA'
        # print wfsa

        parser = Earley(wcfg, wfsa)
        status, R = parser.do('[S]', '[GOAL]')
        if not status:
            print 'NO PARSE FOUND'
            continue
        forest = FrozenWCFG(R)

        print '# FOREST'
        print forest
        print

        top_sort = TopSort(forest)
        sorted_forest = top_sort.top_sort()

        # print "\nSORTED FOREST", sorted_forest

        print "\n------------------------------------- \nTOP SORTED:\n"
        rev_l = reversed(sorted_forest)
        for meh in rev_l:
            for r in forest:
                if r.lhs == meh:
                    print r

        inside = Inside(forest, sorted_forest)
        inside_prob = inside.inside()

        print "\n------------------------------------- \nINSIDE PROBS:\n"
        for prob, v in inside_prob.iteritems():
            print prob, v

        gen_sampling = GeneralisedSampling(forest, inside_prob)
        sampled = gen_sampling.sample('[GOAL]')

        print "\n------------------------------------- \nSAMPLED DERIVATION:\n"
        for s in sampled:
            print s


        """--------------------------------------------------------------
        Temporary, only works with examples/cfg and sentence: "the cat drinks"
        It calculates the ratio between the two possible derivations,
        for checking purposes.
        """
        """
        print "\n\n-------------------------------------------------------------"
        c1 = 0
        c2 = 0

        import time

        start = time.time()
        print "\nBEGIN TIME "

        gen_sampling = GeneralisedSampling(forest, inside_prob)
        for i in range(10000):

            sampled = gen_sampling.sample()

            if str(sampled[1]) == '[S,0-3] -> [NP,0-2] [VP,2-3] (-0.3566)':
                c1 += 1

            elif str(sampled[1]) == '[S,0-3] -> [NP,0-3] (-1.2039)':
                c2 += 2

        print "DER 1 ([S,0-3] -> [NP,0-2] [VP,2-3] (-0.3566) . . . ) occurs: ", c1
        print "DER 2 ([S,0-3] -> [NP,0-3] (-1.2039) . . . ) occurs: ", c2

        ratio_c1 = (float(c1) / (c1 + c2)) * 100
        ratio_c2 = (float(c2) / (c1 + c2)) * 100
        print "Ratio: Der 1: ", ratio_c1, "%"
        print "Ratio: Der 2: ", ratio_c2, "%"

        end = time.time()
        print "\nEND TIME = ", end - start
        ------------------------------------------------------------------"""


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
    #parser.add_argument('output', nargs='?',
    #        type=argparse.FileType('w'), default=sys.stdout,
    #        help='parse trees')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
