__author__ = 'Iason'

import argparse
import sys

from reader import load_grammar
from wcfg import WCFG
from symbol import make_nonterminal
from wfsa import make_linear_fsa
from earley import Earley
from topSort import TopSort
from inside import Inside
from generalisedSampling import GeneralisedSampling


"""
Sample a derivation given a wcfg and a wfsa, with exact sampling, a
form of MC-sampling
"""
def exact_sample(wcfg, wfsa, root='[S]', goal='[GOAL]', n=1):
    samples = dict()

    print >> sys.stderr, 'Parsing...'
    parser = Earley(wcfg, wfsa)
    forest = parser.do(root, goal)

    if not forest:
        print 'NO PARSE FOUND'
        return False
    else:
        print >> sys.stderr, 'Sampling...'
        # sort the forest
        top_sort = TopSort(forest)
        sorted_forest = top_sort.top_sort()

        # calculate the inside weight of the sorted forest
        inside = Inside(forest, sorted_forest)
        inside_prob = inside.inside()

        gen_sampling = GeneralisedSampling(forest, inside_prob)

        it = 0
        while sum(samples.values()) < n:
            it += 1
            if it % 10 == 0:
                print it, "/", n

            # retrieve a random derivation, with respect to the inside weight distribution
            d = gen_sampling.sample(goal)

            if str(d) in samples:
                samples[str(d)] += 1
            else:
                samples[str(d)] = 1

    print "\nDerivation with their occurrences : "
    for der, occ in samples.iteritems():
        print der, occ




def main(args):
    print >> sys.stderr, 'Loading grammar'
    wcfg = load_grammar(args.grammar, args.grammarfmt)
    #print 'GRAMMAR \n', wcfg
    print >> sys.stderr, ' %d rules' % len(wcfg)

    start_symbol = make_nonterminal(args.start)
    goal_symbol = make_nonterminal(args.goal)
    for input_str in args.input:
        wfsa = make_linear_fsa(input_str)
        # print 'FSA\n', wfsa

        import time
        start = time.time()
        
        # exact_sample(wcfg, wfsa, '[S]', '[GOAL]', 10)
        exact_sample(wcfg, wfsa, start_symbol, goal_symbol, args.n)

        end = time.time()
        print "DURATION  = ", end - start



def argparser():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(prog='exact_sampling')

    parser.description = 'Earley parser'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('grammar',
            type=str,
            help='path to CFG rules (or prefix in case of discodop format)')
    parser.add_argument('input', nargs='?',
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus (one sentence per line)')
    parser.add_argument('--start',
            type=str, default='S', 
            help="start symbol of the grammar")
    parser.add_argument('--goal',
            type=str, default='GOAL', 
            help="goal symbol for intersection")
    parser.add_argument('--grammarfmt',
            type=str, default='bar', choices=['bar', 'discodop'],
            help="grammar format ('bar' is the native format)")
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    parser.add_argument('n',
                        type=int,
                        help='The amount of samples')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
