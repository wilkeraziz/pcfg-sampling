"""
@author wilkeraziz
@author Iason
"""

import argparse
import sys

from wcfg import WCFG, read_grammar_rules
from wfsa import make_linear_fsa
from earley import Earley
from sliced_earley import SlicedEarley
from topSort import TopSort
from inside import Inside
from sliced_inside import SlicedInside
from generalisedSampling import GeneralisedSampling
from symbol import parse_annotated_nonterminal

"""
Sample N derivations in maximum K iterations, with method M
M can either be:
    - full: MC-sampling
    - slided: MCMC-sampling
"""
def sample_n(wcfg, wfsa, n=100, m='full', k=1000, a=0.1, b=1):
    conditions = dict()
    samples = dict()

    it = 0
    while sum(samples.values()) < n and it < k:

        """ Question 1: the slice variables are always reset after each run of Earley right?"""
        # reset the slice variables after each run
        slice_variables = dict()

        # print "ITERATION = ", it
        it += 1

        d = sample(wcfg, wfsa, '[GOAL]', m, slice_variables, conditions, a, b)

        if d is not False:
            conditions = update_conditions(d, conditions)

            if str(d) in samples:
                samples[str(d)] += 1
            else:
                samples[str(d)] = 1

    print "\nDerivation with their occurrences : "
    for der, occ in samples.iteritems():
        print der, occ

    print "\nCount failed derivations: ", it - sum(samples.values())

"""
update conditions: the probability of each state of the previous derivation is assigned
to the condition of that state
"""
def update_conditions(d, conditions):
    """ Question 2: only update/overwrite the conditions from the previous derivation
    or completely reset all conditions before updating them? """
    for rule in d:
        conditions[parse_annotated_nonterminal(rule.lhs)] = rule.log_prob
    return conditions

"""
Sample a derivation given a wcfg and a wfsa, with method M
M can either be:
    - full: MC-sampling
    - slided: MCMC-sampling
"""
def sample(wcfg, wfsa, goal='[GOAL]', m='full', slice_variables=dict(), conditions=dict(), a=0.1, b=1):
    if m == 'sliced':
        parser = SlicedEarley(wcfg, wfsa, slice_variables, conditions, a, b)
    else:
        parser = Earley(wcfg, wfsa)

    forest = parser.do('[S]', '[GOAL]')

    if not forest:
        # print 'NO PARSE FOUND'
        return False

    else:
        # sort the forest
        top_sort = TopSort(forest)
        sorted_forest = top_sort.top_sort()

        # calculate the inside weight of the sorted forest
        if m == 'sliced':
            inside = SlicedInside(forest, sorted_forest, slice_variables, goal, a, b)
        else:
            inside = Inside(forest, sorted_forest)

        inside_prob = inside.inside()

        # retrieve a random derivation, with respect to the inside weight distribution
        gen_sampling = GeneralisedSampling(forest, inside_prob)
        d = gen_sampling.sample(goal)

        return d


def main(args):
    wcfg = WCFG(read_grammar_rules(args.grammar))

    # scale parameters for the beta function
    a = 0.1
    b = 1

    # print 'GRAMMAR'
    # print wcfg

    for input_str in args.input:
        wfsa = make_linear_fsa(input_str)
        # print 'FSA'
        # print wfsa

        # import time
        # start = time.time()

        sample_n(wcfg, wfsa, args.n, args.method, args.k, a, b)
        # sample_n(wcfg, wfsa, 1, "sliced", 100, a, b)
        # sample(wcfg, wfsa, '[GOAL]', 'sliced', a, b)

        # end = time.time()
        # print "DURATION FULL = ", end - start



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
    parser.add_argument('method',
                        help='Determine the sampling method, "full"'
                             ' for regular MC-sampling or "sliced" for MCMC-sampling. Defualt is "full" ')
    parser.add_argument('n',
                        type=int,
                        help='The amount of samples')
    parser.add_argument('k',
                        type=int,
                        help='The maximum amount of iterations to find "n" samples')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
