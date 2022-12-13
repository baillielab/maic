import logging

import numpy

from .entity import Entity
from .entitylist import ExponentialEntityList
from typing import MutableSequence, Sequence

from maic.types import Corrector

from maic.io.cv_dumper import CrossValidationDumper
from maic.io.cv_plotter import CrossValidationPlotter

POST_ITERATION_CALLBACK = 'iteration'

logging.basicConfig()
logger = logging.getLogger(__name__)


class CrossValidation(object):
    """A class to perform the cross validation itself.
    Repeatedly loop around the lists and the entities until such time as we
    reach convergence (as determined by the threshold value) or we exceed
    the maximum number of iterations."""

    def __init__(self, entities: MutableSequence[Entity], entity_lists: MutableSequence[ExponentialEntityList], threshold: float, max_iterations: int,
                 transform_methods:MutableSequence[Corrector]=None):
        """Create a new CrossValidation object passing in the Entity and
        EntityList objects and all the settings required to run the
        analysis. Fail if any of the supplied values are missing.
        :type transform_methods: List
        """
        assert entities
        self.entities = entities
        assert entity_lists
        self.entity_lists = entity_lists
        assert threshold
        self.threshold = threshold
        assert max_iterations
        self.max_iterations = max_iterations
        self._fake_entities_seen = {}
        self._fake_entities = []
        self.transform_methods = transform_methods
        self.plotter: CrossValidationPlotter = None
        self.callbacks:dict[str, Sequence[CrossValidationDumper]] = {POST_ITERATION_CALLBACK: []}

    def run(self):
        """Run the analysis."""

        self.run_analysis()
        for entity in self.entities:
            entity.calculate_final_corrected_scores(
                methods=self.transform_methods)

    # unused
    def replace_list(self, list_to_replace, replacement):
        """Replace a list in our set with another one. Because of list
        iterators in Python not coping with the underlying list being
        modified as we process, we need to make sure that the new item gets
        dropped into the same slot in the list as the old one."""

        # If the old item is in the list and the new one is not...
        if list_to_replace in self.entity_lists:
            if replacement not in self.entity_lists:
                idx = self.entity_lists.index(list_to_replace)

                # Tell everything in the list being replaced to forget that it
                # ever knew about the list
                list_to_replace.tell_entities_to_forget()

                # Tell everything in the list being used to re-awaken all its
                # entities
                replacement.tell_entities_to_remember()

                # Replace the old list with the new one
                self.entity_lists[idx] = replacement

    def run_analysis(self):
        """Perform the logic of the cross validation, repeatedly asking
        entities and lists to update their weights/scores until the biggest
        change in the list scores is less than the specified threshold or we
        pass the pre-defined maximum number of iterations.
        NOTE: we update entities first to seed the process, otherwise the
        first iteration produces no change in list weights and the cycle
        stops prematurely.
        As a safety issue, reset everything before we start"""
        for entity_list in self.entity_lists:
            entity_list.reset()
        for entity in self.entities:
            entity.reset()
        for entity in self._fake_entities:
            entity.reset()

        delta = self.threshold + 1
        counter = self.max_iterations
        iteration = 0
        while counter > 0 and delta > self.threshold:
            delta = 0
            counter = counter - 1
            iteration += 1
            # print(iteration,delta)
            for entity in self.entities:  # TODO consolidate these two
                entity.calculate_new_score()
            for entity in self._fake_entities:
                entity.calculate_new_score()
            for entity_list in self.entity_lists:
                delta = max(delta, abs(entity_list.calculate_new_weight()))
            if self.plotter:
                self.plotter.plot_cross_validation(self,
                                                   iteration_number=iteration)
            # pass control to everything that has registered an interest
            for callback in self.callbacks[POST_ITERATION_CALLBACK]:
                callback.do_callback(self, iteration)
            logger.info(
                "{iterations} iterations complete - delta = {delta}".format(
                    iterations=(self.max_iterations - counter), delta=delta))

    def register_callback(self, callback_type, callback_object: CrossValidationDumper):
        """Register an object to be called when a certain phase of the code
        execution is reached. The registered callback_object must have a
        method called 'do_callback' that takes two arguments. The first is
        the CrossValidation object. The second is context dependent. For an
        iteration-related callback, the second argument is the iteration
        number"""
        if callback_type in self.callbacks:
            self.callbacks[callback_type].append(callback_object)
        else:
            logger.warning("Unknown callback type specified ({}). Ignoring "
                           "object {}".format(callback_type, callback_object))

    # unused - only used in testing
    def code_string(self):
        """Generate a string that describes the set of data that we have been
        given to work with."""
        strings_by_category = {}
        for entity_list in self.entity_lists:
            category = entity_list.category
            if category not in strings_by_category:
                strings_by_category[category] = []
            strings_by_category[category].append(entity_list.code_string())
        out_list = []
        for category in sorted(strings_by_category.keys()):
            out_list.append('.'.join(sorted(strings_by_category[category])))
        return '|'.join(out_list)

    # unused - only used in testing 
    def summary_data(self):
        """Calculate and return summary data from the Entities in this
        analysis"""
        scores = [x.score for x in self.entities]
        average = numpy.average(scores)
        stdev = numpy.std(scores)
        return average, stdev

    # unused
    def get_or_create_entity(self, n):
        """Get an Entity"""
        if n < len(self.entities):
            return self.entities[n]
        elif n in self._fake_entities_seen:
            return self._fake_entities_seen[n]
        else:
            ent = Entity("Fake Entity " + str(n))
            self._fake_entities_seen[n] = ent
            self._fake_entities.append(ent)
            return ent


def build_cross_validation(lines, entity_list_builder, stability,
                           max_iterations, transform_methods=None) -> CrossValidation:
    """Given a set of input data lines, a pre-configured EntityListBuilder
    and some values for stability and max_iterations, return a new
    CrossValidation analysis object"""
    list_of_lists = []
    for line in lines:
        list_of_lists.append(
            entity_list_builder.build_list_from_string(line))
        logger.debug("line read '%s'" % line)
    # Grab a list of all known Entities from the EntityListBuilder
    all_entities = entity_list_builder.entities()
    logger.info("Input file read, list of Entities secured")
    # Make a new CrossValidation object using the list of Entities,
    # the list of EntityLists, a value for threshold and a value for
    # max_iterations
    cross_validation = CrossValidation(all_entities, list_of_lists,
                                       stability,
                                       max_iterations,
                                       transform_methods=transform_methods)
    return cross_validation
