# coding=utf-8
from __future__ import print_function
import logging
import sys
import numpy
import json
from baseline import get_baseline_from_store, put_baseline_to_store, Baseline
from cross_validation import build_cross_validation, \
    random_data_matching_code_string
from entitylist_builder import EntityListBuilder
from file_reader import FileReader
from genescores_dumper import GeneScoresDumper, AllScoresGeneScoresDumper
from options import get_parsed_options
import pandas as pd
import numpy as np

class Maic(object):
    """Class to manage the cross validation analysis and all parameters
    surrounding it"""
    __version = 1.0

    def __init__(self):
        pass

    def get_appropriate_baseline(self, cross_validation, options):
        """Get a baseline for the supplied CrossValidation object. If no
        matching Baseline is found in the pre-calculated store, then one
        will be calculated (and stored)"""
        # Grab a logger for this function to use
        logger = logging.getLogger(__name__)
        logger.info("Trying to get a baseline to match the parameters")
        baseline = get_baseline_from_store(options.baseline, Maic.__version,
                                           cross_validation.code_string(),
                                           options.weight_function,
                                           options.num_perms)
        if baseline is None:
            logger.info("Didn't find a baseline - going to calculate one")
            baseline = self.calculate_baseline(cross_validation, options)
            logger.info("Saving the new baseline to disk")
            put_baseline_to_store(options.baseline, Maic.__version, baseline)
        return baseline

    def calculate_baseline(self, cross_validation, options):
        """Perform a number of data set simulations and calculate a baseline
        from them"""
        # Grab a logger for this function to use
        logger = logging.getLogger(__name__)
        logger.info("Generating random data sets to calculate a baseline")
        code_string = cross_validation.code_string()
        baseline_analyses = []
        baseline_summaries = []

        # Build an appropriate number of random data sets matching the
        # actual input data supplied
        for n in range(0, options.num_perms):
            base_elb = EntityListBuilder(options.weight_function,
                                         options.max_input_len)
            random_data = random_data_matching_code_string(code_string,
                                                           options.random_source_len)
            cv = build_cross_validation(random_data, base_elb,
                                        options.stability,
                                        options.max_iterations)
            baseline_analyses.append(cv)

        # Run each analysis and snaffle the scores
        baseline_scores = []
        for baseline_analysis in baseline_analyses:
            baseline_analysis.run()
            baseline_scores += [x.score for x in baseline_analysis.entities]

        # Then calculate the mean and stdev and record a Baseline object
        average = numpy.average(baseline_scores)
        stdev = numpy.std(baseline_scores)

        baseline = Baseline(code_string, average, stdev, options.num_perms,
                            options.weight_function)
        logger.debug("Calculated a new Baseline:\n%s" % baseline)
        return baseline

    def run(self, args):
        options = get_parsed_options(args)
        # Set up logging as requested by the options
        logging.basicConfig()
        root_logger = logging.getLogger('')
        root_logger.setLevel(options.logging_level)
        # Grab a logger for this class to use
        logger = logging.getLogger(__name__)
        # Create a new FileReader object
        file_reader = FileReader()
        # Tell it to read the file, passing in the path to the file as an
        # argument
        logger.info("Reading the input data file")
        file_reader.read_file(options.filename)
        # Make a new EntityListBuilder
        elb = EntityListBuilder(options.weight_function, options.max_input_len)
        # Use the lines read and the EntityListBuilder to create a
        # CrossValidation analysis object
        cross_validation = build_cross_validation(file_reader.list_lines, 
                                                  elb,
                                                  options.stability,
                                                  options.max_iterations,
                                                  options.twiddle_method)
        logger.info("CrossValidation analysis set up")
        cross_validation.run()
        logger.info("CrossValidation analysis complete")

        # [JKB] is this vestigial?
        baseline = None
        if options.baseline:
            baseline = self.get_appropriate_baseline(cross_validation, options)
        else:
            logger.info("Not using baseline because it was not "
                        "requested")

        logger.info("Dumping gene scores")
        gsd = AllScoresGeneScoresDumper(cross_validation)
        gsd.dump(options.gene_score_output_file)


if __name__ == '__main__':
    app = Maic()
    app.run(sys.argv[1:])


