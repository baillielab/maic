# -*- coding: utf-8 -*-
"""Code relating to configuration options

Classes and code relating to the management of configuration options in the
integrative cross-validation code.
"""
import argparse
import logging
import os
from time import strftime


def get_parsed_options(args=None):
    """Parse any command line arguments and convert them into a Namespace
    object that we can query as required elsewhere in the code
    """
    parser = argparse.ArgumentParser()
    #
    parser.add_argument('-f', '--filename', default=None,
                        help='path to the file containing data to be analysed')
    #
    parser.add_argument('-o', '--output-folder', default=None,
                        help='path to the folder in which to write the '
                             'results files')
    #
    parser.add_argument('-p', '--plot', default=False, action='store_true',
                        help='draw plots for each list at each iteration')
    #
    parser.add_argument('-d', '--dump-scores', default=False,
                        action='store_true',
                        dest='dump',
                        help='dump maic scores at each iteration')
    #
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase the detail of logging messages.')
    #
    parser.add_argument('-q', '--quiet', action='count', default=0,
                        help='decrease the detail of logging messages '
                             '(overrides the -v/--verbose flag)')
    #
    parsed_options = parser.parse_args(args)

    # build a default output_folder if required and if we can
    if not parsed_options.output_folder:
        if parsed_options.filename:
            timestamp = strftime("%Y-%m-%d--%H-%M")
            base = os.path.splitext(parsed_options.filename)[0]
            parsed_options.output_folder = base + '-' + timestamp

    # Set the non-negotiable options
    parsed_options.max_input_len = 2000
    parsed_options.weight_function = 'exponential'
    parsed_options.random_source_len = 20000
    parsed_options.stability = 0.01
    parsed_options.max_iterations = 100
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
