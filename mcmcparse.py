__author__ = 'Iason'

import argparse
import sys
import logging

from reader import load_grammar
from collections import defaultdict
from sentence import make_sentence
from sliced_earley import SlicedEarley
from topsort import top_sort
import sliced_inside
from generalisedSampling import GeneralisedSampling
from symbol import parse_annotated_nonterminal
import time

"""
Sample N derivations in maximum K iterations with Slice Sampling
"""
def sliced_sampling(wcfg, wfsa, root='[S]', goal='[GOAL]', n=100, k=1000, a=0.1, b=1):
    samples = defaultdict(int)
    conditions = dict()

    # the previous derivation, initially False
    prev_d = False

    it = 0
    while sum(samples.values()) < n and it < k:
        it += 1
        if it % 10 == 0:
                print it, "/", n

        d = sliced_sample(wcfg, wfsa, conditions, root, goal, a, b)

        if d is not False:
            # often the previous derivation is similar to the new sampled derivation
            # updating the conditions would be a waste of time, since they remain the same
            if not d == prev_d:
                conditions = update_conditions(d)

            samples[str(d)] += 1

        prev_d = d

    print "\nDerivation with their occurrences : "
    for der, occ in samples.iteritems():
        print der, occ

    print "\nCount failed derivations: ", it - sum(samples.values())

"""
update conditions: the probability of each state of the previous derivation is assigned
to the condition of that state
"""
def update_conditions(d):
    conditions = dict()
    for rule in d:
        conditions[parse_annotated_nonterminal(rule.lhs)] = rule.log_prob
    return conditions

"""
Sample a derivation given a wcfg and a wfsa, with Slice Sampling, a
form of MCMC-sampling
"""
def sliced_sample(wcfg, wfsa, conditions, root='[S]', goal='[GOAL]', a=0.1, b=1):
    slice_variables = dict()

    logging.info('Parsing...')
    parser = SlicedEarley(wcfg, wfsa, slice_variables, conditions, a, b)
    forest = parser.do(root, goal)

    if not forest:
        logging.debug('NO PARSE FOUND')
        return False

    else:
        logging.info('Forest: rules=%d', len(forest))
        logging.debug('Topsorting...')

        # sort the forest
        sorted_nodes = top_sort(forest)

        # calculate the inside weight of the sorted forest
        logging.debug('Inside...')
        inside_prob = sliced_inside.sliced_inside(forest, sorted_nodes, slice_variables, goal, a, b)

        logging.debug('Sampling...')
        # retrieve a random derivation, with respect to the inside weight distribution
        gen_sampling = GeneralisedSampling(forest, inside_prob)
        d = gen_sampling.sample(goal)

        return d


def main(args):

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(message)s')

    # wcfg = WCFG(read_grammar_rules(args.grammar))

    logging.info('Loading grammar...')
    wcfg = load_grammar(args.grammar, args.grammarfmt)
    logging.info(' %d rules', len(wcfg))

    # print 'GRAMMAR\n', wfg

    for input_str in args.input:
        sentence, extra_rules = make_sentence(input_str, wcfg.terminals, args.unkmodel, args.default_symbol)
        wcfg.update(extra_rules)

        start = time.time()

        sliced_sampling(wcfg, sentence.fsa, '[S]', '[GOAL]', args.samples, args.max, args.a, args.b)
        # sliced_sampling(wcfg, wfsa, '[S]', '[GOAL]', 1000, 20000, 0.1, 1)

        end = time.time()
        print "DURATION  = ", end - start



def argparser():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(prog='mcmcparse')

    parser.description = 'MCMC Earley parser'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('grammar',
            type=str,
            help='path to CFG rules (or prefix in case of discodop format)')
    parser.add_argument('input', nargs='?',
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus (one sentence per line)')
    parser.add_argument('--samples',
                        type=int, default=100,
                        help='The number of samples')
    parser.add_argument('--max',
                        type=int, default=200,
                        help='The maximum number of iterations')
    parser.add_argument('-a',
                        type=float, default=0.1,
                        help='a, first Beta parameter')
    parser.add_argument('-b',
                        type=float, default=1.0,
                        help='b, second Beta parameter')
    parser.add_argument('--unkmodel',
            type=str, default=None,
            choices=['passthrough', 'stfdbase', 'stfd4', 'stfd6'],
            help="unknown word model")
    parser.add_argument('--default-symbol',
            type=str, default='X',
            help='default nonterminal (use for pass-through rules)')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    parser.add_argument('--grammarfmt',
            type=str, default='bar', choices=['bar', 'discodop'],
            help="grammar format ('bar' is the native format)")

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
