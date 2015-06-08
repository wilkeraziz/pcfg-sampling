__author__ = 'Iason'

import argparse
import logging
import sys

from reader import load_grammar
from collections import defaultdict
from symbol import make_nonterminal
from earley import Earley
from topsort import top_sort
from sentence import make_sentence
import inference
from generalisedSampling import GeneralisedSampling


"""
Sample a derivation given a wcfg and a wfsa, with exact sampling, a
form of MC-sampling
"""
def exact_sample(wcfg, wfsa, root='[S]', goal='[GOAL]', n=1):
    samples = defaultdict(int)

    logging.info('Parsing...')
    parser = Earley(wcfg, wfsa)
    forest = parser.do(root, goal)

    if not forest:
        print 'NO PARSE FOUND'
        return False
    else:

        logging.info('Forest: rules=%d', len(forest))

        logging.debug('Topsorting...')
        # sort the forest
        sorted_nodes = top_sort(forest)

        # calculate the inside weight of the sorted forest
        logging.debug('Inside...')
        inside_prob = inference.inside(forest, sorted_nodes)

        gen_sampling = GeneralisedSampling(forest, inside_prob)

        logging.debug('Sampling...')
        it = 0
        while sum(samples.values()) < n:
            it += 1
            if it % 10 == 0:
                print it, "/", n

            # retrieve a random derivation, with respect to the inside weight distribution
            d = gen_sampling.sample(goal)

            samples[str(d)] += 1

    print "\nDerivation with their occurrences : "
    for der, occ in samples.iteritems():
        print der, occ




def main(args):

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(message)s')

    logging.info('Loading grammar...')
    wcfg = load_grammar(args.grammar, args.grammarfmt)
    logging.info(' %d rules', len(wcfg))
    #print 'GRAMMAR \n', wcfg


    start_symbol = make_nonterminal(args.start)
    goal_symbol = make_nonterminal(args.goal)
    for input_str in args.input:
        sentence, extra_rules = make_sentence(input_str, wcfg.terminals, args.unkmodel, args.default_symbol)
        wcfg.update(extra_rules)

        # print 'FSA\n', wfsa

        import time
        start = time.time()

        exact_sample(wcfg, sentence.fsa, start_symbol, goal_symbol, args.samples)

        end = time.time()
        print "DURATION  = ", end - start



def argparser():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(prog='parse')

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

    parser.add_argument('--samples',
                        type=int, default=100,
                        help='The number of samples')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())
