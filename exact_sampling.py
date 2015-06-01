__author__ = 'Iason'

import argparse
import sys

from wcfg import WCFG, read_grammar_rules
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

    parser = Earley(wcfg, wfsa)
    forest = parser.do(root, goal)

    if not forest:
        print 'NO PARSE FOUND'
        return False
    else:
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
            if it % (n / 10) == 0:
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
    wcfg = WCFG(read_grammar_rules(args.grammar))
    # print 'GRAMMAR \n', wcfg

    for input_str in args.input:
        wfsa = make_linear_fsa(input_str)
        # print 'FSA\n', wfsa

        import time
        start = time.time()

        # exact_sample(wcfg, wfsa, '[S]', '[GOAL]', 10)
        exact_sample(wcfg, wfsa, '[S]', '[GOAL]', args.n)

        end = time.time()
        print "DURATION  = ", end - start



def argparser():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(prog='exact_sampling')

    parser.description = 'Earley parser'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('grammar',
            type=argparse.FileType('r'),
            help='CFG rules')
    parser.add_argument('input', nargs='?',
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus (one sentence per line)')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    parser.add_argument('n',
                        type=int,
                        help='The amount of samples')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
