"""
:Authors: - Iason
"""

import pstats
import argparse


def main(args):
    p = pstats.Stats(args.pstats)
    stats = {}

    stats['runtime'] = p.total_tt
    stats['file_name'] = args.pstats

    # MCMC STATS
    if args.parser_type == 'mcmc':
        for k, v in p.stats.iteritems():
            if 'sliced_nederhof.py' in k[0]:
                if 'do' in k[2]:
                    stats['parse_time_total'] = v[3]
                    stats['parse_time_per_call'] = v[3] / v[0]
            elif 'sliced_sample' in k:
                stats['sample_time_total'] = v[3]
                stats['sample_time_per_call'] = v[3] / v[1]
            elif 'initialise' in k:
                stats['first_sample_time'] = v[3] / v[1]
    # MC STATS
    elif args.parser_type == 'mc':
        for k, v in p.stats.iteritems():
            if 'nederhof.py' in k[0]:
                if 'do' in k[2]:
                    stats['parse_time_total'] = v[3]
                    stats['parse_time_per_call'] = v[3] / v[0]
            elif 'exact_sample' in k:
                stats['sample_time_total'] = v[3]
                stats['sample_time_per_call'] = v[3] / v[1]
    else:
        print "Parser Type unknown!"

    print "\n\n_______________________________________\n________________STATS__________________\n"
    print "Filename = ", stats['file_name']
    print "Runtime = ", stats['runtime']
    print "Total sample time = ", stats['sample_time_total']
    print "Per call sample time = ", stats['sample_time_per_call']
    print "Total parse time = ", stats['parse_time_total']
    print "Per call parse time = ", stats['parse_time_per_call']
    if args.parser_type == 'mcmc':
        print "First sample time = ", stats['first_sample_time']


def argparser():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(prog='get_stats')

    parser.description = 'Get cProfile stats'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('--pstats',
            type=str,
            help='path to cProfile stats')
    parser.add_argument('--parser_type',
            type=str, default='mc', choices=['mc', 'mcmc'],
            help='Tyope of the parser')

    return parser

if __name__ == '__main__':
    main(argparser().parse_args())