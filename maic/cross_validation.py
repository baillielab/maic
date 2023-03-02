import logging
import numpy

POST_ITERATION_CALLBACK = 'iteration'

logging.basicConfig()
logger = logging.getLogger(__name__)


class CrossValidation(object):
    """A class to perform the cross validation itself.
    Repeatedly loop around the lists and the entities until such time as we
    reach convergence (as determined by the threshold value) or we exceed
    the maximum number of iterations."""

    def __init__(self, entities, entity_lists, threshold, max_iterations,
                 transform_methods=None):
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
        self.transform_methods = transform_methods
        self.plotter = None
        self.callbacks = {POST_ITERATION_CALLBACK: []}

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

        delta = self.threshold + 1
        counter = self.max_iterations
        iteration = 0
        while counter > 0 and delta > self.threshold:
            delta = 0
            counter = counter - 1
            iteration += 1
            # print(iteration,delta)
            for entity in self.entities:
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

    def register_callback(self, callback_type, callback_object):
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

    def summary_data(self):
        """Calculate and return summary data from the Entities in this
        analysis
        returns: a 2-tuple of `numpy.floating` values: the first is the *average*, the second is the *standard deviation*
        """
        scores = [x.score for x in self.entities]
        average = numpy.average(scores)
        stdev = numpy.std(scores)
        return average, stdev
