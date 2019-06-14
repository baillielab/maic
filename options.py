# -*- coding: utf-8 -*-
"""Code relating to configuration options

Classes and code relating to the management of configuration options in the
integrative cross-validation code.
"""
import argparse
import logging
import sys

CHOP_THRESHOLD_RANGE = "{0.0..1.0}"

TWIDDLE_STANDARD_OPTIONS = ['none', 'mean', 'z-transform']
TWIDDLE_EXTENDED_OPTIONS = ['pow_', 'scale_']

# TODO identify the bug in argparse that breaks if this is used as a metavar
TWIDDLE_OPTIONS_HELP = ", ".join(
    TWIDDLE_STANDARD_OPTIONS + [x + "\d+[\.\d+]" for x in
                                TWIDDLE_EXTENDED_OPTIONS])


def get_parsed_options(args=None):
    """Parse any command line arguments and convert them into a Namespace
    object that we can query as required elsewhere in the code
    """
    parser = argparse.ArgumentParser()
    #
    parser.add_argument('-f', '--filename', default=None,
                        help='path to the file containing data to be analysed')
    #
    parser.add_argument('-z', '--z', action="store_true", default=False,
                        help='default=False. Use a z-score from permuted '
                             'lists')
    #
    parser.add_argument('-t', '--twiddle-method', default='none', 
                        help='temporarily disabled checks')
    '''
    parser.add_argument('-t', '--twiddle-method', default='none', choices=[
        TwiddleMethodOptionsChecker(TWIDDLE_STANDARD_OPTIONS,
                                    TWIDDLE_EXTENDED_OPTIONS)],
                        metavar="['none', 'mean', 'z-transform', 'pow_<N>', "
                                "'scale_<N>'] where <N> is a valid number",
                        # metavar = TWIDDLE_OPTIONS_HELP,
                        help='twiddle method to adjust scores')
    '''
    #
    parser.add_argument('-b', '--baseline', const="${HOME}/.maic-baselines",
                        default=None, nargs='?',
                        help='Correct scores using a baseline calculated '
                             'from random data matching the input data set. '
                             'Optionally specify the path to a file in which '
                             'pre-calculated baselines are stored (default '
                             'is ${HOME}/.maic-baselines.txt.')
    #
    parser.add_argument('-g', '--gene-score-output-file', default=None,
                        type=argparse.FileType('w'), nargs='?',
                        const=sys.stdout)
    #
    # noinspection PyTypeChecker
    parser.add_argument('-c', '--chop-threshold', type=float, default=0.8,
                        choices=[RangeChecker(0.0, 1.0)],
                        metavar=CHOP_THRESHOLD_RANGE,
                        help='0.0 < chop-threshold < 1.0')
    #
    # noinspection PyTypeChecker
    parser.add_argument('-m', '--max-input-len', type=int, default=2000,
                        help='maximum list length to include')
    #
    # noinspection PyTypeChecker
    parser.add_argument('-n', '--num-perms', type=int, default=100,
                        help='number of permutations (to generate z score)')
    #
    parser.add_argument('-e', '--exclude-current-gene', action="store_true",
                        default=False,
                        help='default=False. Less biased but much much '
                             'slower. Does not significantly affect results. ')
    #
    parser.add_argument('-w', '--weight-function', default='knn',
                        choices=['none', 'knn', 'polynomial', 'exponential',
                                 'svr'],
                        help='weighting function to use for ranked lists')
    #
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase the detail of logging messages.')
    #
    parser.add_argument('-q', '--quiet', action='count', default=0,
                        help='decrease the detail of logging messages '
                             '(overrides the -v/--verbose flag)')
    #
    parsed_options = parser.parse_args(args)
    # Set the non-negotiable options
    parsed_options.eliminate_categories = False
    parsed_options.random_source_len = 20000
    parsed_options.stability = 0.01
    parsed_options.max_iterations = 100
    parsed_options.max_rotations = 100
    parsed_options.num_rand_datasets_for_baseline = 10
    parsed_options.logging_level = logging.WARN
    if parsed_options.verbose == 1:
        parsed_options.logging_level = logging.WARN
    elif parsed_options.verbose == 2:
        parsed_options.logging_level = logging.INFO
    elif parsed_options.verbose > 2:
        parsed_options.logging_level = logging.DEBUG
    if parsed_options.quiet == 1:
        parsed_options.logging_level = logging.ERROR
    elif parsed_options.quiet > 1:
        parsed_options.logging_level = logging.CRITICAL
    del parsed_options.verbose
    del parsed_options.quiet
    return parsed_options


class RangeChecker(object):
    """A class to provide range checking for float arguments supplied to our
    argument parser.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return self.start <= other <= self.end

    def __repr__(self):
        return CHOP_THRESHOLD_RANGE


class TwiddleMethodOptionsChecker(object):
    """A class to check the validity of arguments supplied to the argument
    parser when defining the twiddle method"""

    def __init__(self, standard_set, extended_set):
        self.standard_set = standard_set
        self.extended_set = extended_set

    def __eq__(self, other):
        import re
        if other in self.standard_set:
            return True
        for stem in self.extended_set:
            if re.match("^" + stem + "(\\d+)(\\.\\d+)?$", other, re.M):
                return True
        return False
