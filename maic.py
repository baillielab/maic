# coding=utf-8
from __future__ import print_function

import logging
import os
import re
import sys
from time import strftime

from maic.cross_validation import build_cross_validation, POST_ITERATION_CALLBACK
from cv_dumper import CrossValidationDumper
from cv_plotter import CrossValidationPlotter
from maic.entitylist_builder import EntityListBuilder
from maic.io.file_reader import FileReader
from maic.io.genescores_dumper import AllScoresGeneScoresDumper, \
    IterationAwareGeneScoresDumper
from maic.cli.options import get_parsed_options


class Maic(object):
    """Class to manage the cross validation analysis and all parameters
    surrounding it"""
    __version = 1.0

    def __init__(self):
        pass

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
        cross_validation = build_cross_validation(file_reader.list_lines, elb,
                                                  options.stability,
                                                  options.max_iterations)
        logger.info("CrossValidation analysis set up")

        output_folder = self.make_output_folder(options.output_folder)
        logger.info("Output folder created")

        if options.plot:
            images_folder = self.make_output_folder(
                os.sep.join([output_folder, "images"]))
            cross_validation.plotter = CrossValidationPlotter(images_folder)

        if options.dump:
            dump_folder = self.make_output_folder(
                os.sep.join([output_folder, "scores"])
            )
            iteration_aware_dumper = IterationAwareGeneScoresDumper(
                cross_validation, dump_folder)
            cross_validation_dumper = CrossValidationDumper(
                dumper=iteration_aware_dumper)
            cross_validation.register_callback(POST_ITERATION_CALLBACK,
                                               cross_validation_dumper)


        logger.info("Running the CrossValidation analysis")
        cross_validation.run()
        logger.info("CrossValidation analysis complete")

        logger.info("Dumping gene scores")
        gsd = AllScoresGeneScoresDumper(cross_validation, output_folder)
        gsd.dump()
        gsd.dataset_feature_check_to_choice_methods()

    def make_output_folder(self, output_folder):
        """Given a requested output folder, create it and return the full
        path as a String. If the output folder is empty or not defined,
        return the empty string. If the output folder already exists and
        does not already end with something that looks like a timestamp then
        try to add a timestamp to it."""

        # Grab a logger for this function to use
        logger = logging.getLogger(__name__)

        if not output_folder:
            logger.info("No output folder specified - will use the current "
                        "directory")
            return ""

        # Don't try to create the current folder. Do try to make a directory
        # for all other instances
        if output_folder != '.':
            try:
                os.makedirs(output_folder)
            except OSError as exc:
                if not re.search(r'\d{4}(-\d{2}){2}-(-\d{2}){2}/?$',
                                 output_folder, re.S):
                    logger.warning(
                        "Specified folder (" + output_folder + ") already "
                        "exists - trying to create one with a timestamp")
                    timestamp = strftime("%Y-%m-%d--%H-%M")
                    return self.make_output_folder(
                        output_folder = "{}-{}".format(output_folder,
                                                       timestamp))
                else:
                    raise exc

        # make sure that the string we return will always have a trailing
        # separator (that makes creating the individual files simpler)
        if not re.search(r'^(.*)/$', output_folder, re.S):
            output_folder += os.sep

        return output_folder


if __name__ == '__main__':
    app = Maic()
    app.run(sys.argv[1:])
