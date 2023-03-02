from time import strftime
from .entitylist import EntityList, ExponentialEntityList
from .cross_validation import CrossValidation, POST_ITERATION_CALLBACK

from maic.io.cv_plotter import CrossValidationPlotter
from maic.io.cv_dumper import CrossValidationDumper
from maic.io.genescores_dumper import AllScoresGeneScoresDumper, IterationAwareGeneScoresDumper

from maic.io import Format, read_file

import re
import os
from os.path import join

import logging

logging.basicConfig()

logger = logging.getLogger(__name__)

from json import dump as dumpJSON
from oyaml import dump as dumpYAML

from numpy import zeros, std, max as npmax

class Maic:

    @staticmethod
    def fromfile(filepath, *, 
        format=Format.MAIC, 
        threshold=0.01, 
        maxlistlength=2000, 
        maxiterations=100, 
        output_folder=None, 
        plot=False, 
        dump=False,
    ):
        """
        Construct a MAIC analysis from an input file.
        Parameters (all but filepath are *keyword only*):
        @filepath: the relative or absolute path to the file containing the data.
        @format: the format of the data in the file: MAIC, JSON or YAML (see maic.io.FORMAT)
        @threshold: the maximum change in list weights to indicate result convergence
        @maxlistlength: the maximum number of entities to import for each line in the file (entities beyond this value are discarded *before* analysis).
        @maxiterations: the maximum number of iterations to complete if the list weights do not converge to the @threshold
        @output_folder: the path of the folder in which to record results
        @plot: default False - set True to plot the distribution of scores for each list on each iteration
        @dump: default False - set True to dump the list scores to file for each generation
        """
        elm_lists = read_file(filepath, format=format)

        m = Maic(modellist=elm_lists, threshold=threshold, maxlistlength=maxlistlength, maxiterations=maxiterations)

        if output_folder is not None:
            m.output_folder = output_folder

        if plot:
            m.add_plotter()

        if dump:
            m.add_dumper()

        return m

    @staticmethod
    def fromCLI(options=None):
        """
        Used by maic.cli to run analyses directly from the command line.
        Calls Maic.fromfile, using parameters generated via maic.io.options
        """
        if options is None:
            raise ValueError("Cannot call static method fromCLI() without options argument")

        
        return Maic.fromfile(
            options.filename,
            format=options.type,
            threshold=options.stability,
            maxlistlength=options.max_input_len,
            maxiterations=options.max_iterations,
            output_folder=options.output_folder,
            plot=options.plot,
            dump=options.dump
        )


    def __init__(self, *, 
        modellist, 
        threshold=0.01, 
        maxlistlength=2000, 
        maxiterations=100, 
    ):
        self._entities = {}
        self._lists = []

        for elm in modellist:
            if elm.is_ranked:
                self._lists.append(ExponentialEntityList.frommodel(elm, entities=self._entities, limit=maxlistlength))
            else:
                self._lists.append(EntityList.frommodel(elm, entities=self._entities, limit=maxlistlength))

        self._cv = CrossValidation(list(self._entities.values()), self._lists, threshold, maxiterations)
        self.output_folder = "."
        self._run = False

    @property
    def output_folder(self):
        return self._of

    @output_folder.setter
    def output_folder(self, value):
        """Given a requested output folder, create it and store the full path as a property of this Maic object. 
        If the output folder is empty or not defined,
        return the empty string. If the output folder already exists and
        does not already end with something that looks like a timestamp then
        try to add a timestamp to it."""

        if not value:
            logger.info("No output folder specified - will use the current "
                        "directory")
            value = "."

        # Don't try to create the current folder. Do try to make a directory
        # for all other instances
        if value != '.':
            try:
                os.makedirs(value)
            except OSError as exc:
                if not re.search(r'\d{4}(-\d{2}){2}-(-\d{2}){2}/?$',value, re.S):
                    logger.warning(f"Specified folder ({value}) already exists - trying to create one with a timestamp")
                    timestamp = strftime("%Y-%m-%d--%H-%M")
                    self.output_folder = f"{value}-{timestamp}"
                    return
                else:
                    raise exc

        # make sure that the string we return will always have a trailing
        # separator (that makes creating the individual files simpler)
        if not re.search(r'^(.*)/$', value, re.S):
            value += os.sep

        self._of = value

    def add_plotter(self, plotter=None):
        if plotter is None:
            plotter = CrossValidationPlotter(join(self.output_folder, "images"))

        self._cv.plotter = plotter

    def add_dumper(self, dumper=None):
        if dumper is None:
            dumper = CrossValidationDumper(IterationAwareGeneScoresDumper(self._cv, join(self.output_folder, "scores")))

        self._cv.register_callback(POST_ITERATION_CALLBACK, dumper)

    def run(self, *, dump_result=True):
        if self._run:
            logger.warn("Duplicate run of MAIC analysis: we recommend only running this analysis once.")

        self._cv.run_analysis()
        self._run = True

        if dump_result:
            self.dump_result()

    @property
    def sorted_results(self):
        if not self._run:
            raise RuntimeError("Attempt to retrieve entity scores before analysis has been run.")

        result = []

        for entity in self._cv.entities:
            entity_scores = {
                "name": entity.name,
                "maic_score": entity.transformed_score()
            }

            for lst in self._cv.entity_lists:
                entity_scores[lst.name] = max(0.0, entity.score_from_list(lst))

            entity_scores["contributors"] = ", ".join([f"{k}: {v.name}" for k,v in entity.winning_lists_by_category().items()])

            result.append(entity_scores)
        
        return sorted(result, key=lambda es: es['maic_score'], reverse=True)

    @property
    def methodology_feature_check(self):
        if not self._run:
            raise RuntimeError("Attempt to retrieve dataset features before analysis has been run.")

        recommendations = {
            "MAIC": " Based on the characteristics of your dataset, we have estimated that MAIC is the best algorithm for this analysis! See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this.",
            "BiGbottom": "Warning! Your dataset has the unusual combination of ranked-only data and a small number of sources ({listcount}) included. Based on these features we think you'd get better results from running BiGbottom [https://github.com/xuelilyli/BiG]. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this.",
            "BIRRA": "Warning! Your dataset has the unusual combination of ranked-only data, high heterogeneity and a relatively large number of sources ({listcount}) included. Based on these features we think you'd get better results from running BIRRA [http://www.pitt.edu/~mchikina/BIRRA/]. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this."
        }

        number_of_lists = len(self._cv.entity_lists)
        list_weights0 = zeros(number_of_lists)
        unranked_included = False

        for i, l in enumerate(self._cv.entity_lists):
            if l.is_ranked:
                list_weights0[i] = l.weights_list[0]
            else:
                unranked_included = True

        normalized_weights = list_weights0 / npmax(list_weights0)
        hetro = std(normalized_weights)

        rec = "MAIC"

        if not unranked_included:
            if number_of_lists < 8:
                rec = "BiGbottom"
            elif hetro > 0.12:
                rec = "BIRRA"

        return recommendations[rec].format(listcount=number_of_lists)


    def dump_result(self, *, folder=None, format=Format.MAIC):
        if not self._run:
            raise RuntimeError("Attempt to dump results before analysis has been run.")

        if folder is None:
            folder = self.output_folder

        if format == Format.MAIC:
            gsd = AllScoresGeneScoresDumper(self._cv, folder)
            gsd.dump()
            gsd.dataset_feature_check_to_choice_methods()
        else:
            # retrieve a results dict then dump into JSON or YAML:
            results = {
                "scores": self.sorted_results,
                "methodology": self.methodology_feature_check
            }

            filename = "maic-raw.json" if format == Format.JSON else "maic-raw.yml"

            with open(join(folder, filename), "w+") as f:
                if format == Format.JSON:
                    dumpJSON(results, f)
                elif format == Format.YAML:
                    dumpYAML(results, f)
                else:
                    raise ValueError(f"Unknown file format {format}")

