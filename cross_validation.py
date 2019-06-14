import logging
import re

import numpy

from entity import Entity

logging.basicConfig()
logger = logging.getLogger(__name__)


class CrossValidation(object):
    """A class to perform the cross validation itself.
    Repeatedly loop around the lists and the entities until such time as we
    reach convergence (as determined by the threshold value) or we exceed
    the maximum number of iterations."""

    def __init__(self, entities, entity_lists, threshold, max_iterations,
                 twiddle_method=None):
        """Create a new CrossValidation object passing in the Entity and
        EntityList objects and all the settings required to run the
        analysis. Fail if any of the supplied values are missing.
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
        self.twiddle_method = twiddle_method

    def run(self):
        """Perform the logic of the cross validation, repeatedly asking
        entities and lists to update their weights/scores until the biggest
        change in the list scores is less than the specified threshold or we
        pass the pre-defined maximum number of iterations.
        NOTE: we update entities first to seed the process, otherwise the
        first iteration produces no change in list weights and the cycle
        stops prematurely."""

        # Before we run an analysis, we need to calculate a baseline for
        # each list in the data set. We do that by repeatedly generating
        # random lists of the same size as each list in turn and then
        # run the analysis, recording the scores for the entities involved
        # TODO - pass the number of iterations into the code somehow
        number_of_baseline_runs = 10
        for lst in self.entity_lists:
            code_string = lst.code_string()
            list_to_replace = lst
            baseline_scores = []
            baseline_weights = []
            for i in range(number_of_baseline_runs):
                new_fake_list = self.make_fake_list(lst)
                self.replace_list(list_to_replace, new_fake_list)
                self.run_analysis()
                baseline_scores += [x.score for x in
                                    new_fake_list.get_entities()]
                baseline_weights += [new_fake_list.weight]
                list_to_replace = new_fake_list
            self.replace_list(list_to_replace, lst)
            base_score_mean = numpy.average(baseline_scores)
            base_score_stdev = numpy.std(baseline_scores)
            base_weight_mean = numpy.average(baseline_weights)
            lst.set_baseline(base_score_mean, base_score_stdev,
                             base_weight_mean)
        self.run_analysis()
        for entity in self.entities:
            entity.calculate_new_score(self.twiddle_method)

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
        """Run an actual analysis until max_iterations or until we get
        convergence. As a safety issue, reset everything before we start"""
        for entity_list in self.entity_lists:
            entity_list.reset()
        for entity in self.entities:
            entity.reset()
        for entity in self._fake_entities:
            entity.reset()

        delta = self.threshold + 1
        counter = self.max_iterations
        while counter > 0 and delta > self.threshold:
            delta = 0
            counter = counter - 1
            for entity in self.entities: # TODO consolidate these two
                entity.calculate_new_score()
            for entity in self._fake_entities:
                entity.calculate_new_score()
            for entity_list in self.entity_lists:
                delta = max(delta, entity_list.calculate_new_weight())
            logger.debug(
                "{} iterations complete".format(self.max_iterations - counter))

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
        analysis"""
        scores = [x.score for x in self.entities]
        average = numpy.average(scores)
        stdev = numpy.std(scores)
        return average, stdev

    def make_fake_list(self, lst):
        """Make a new, fake list with random data"""
        _genome_size = 20000 # TODO - pass this value into the code somehow
        new_list = lst.blank_copy()
        new_list.category_name = lst.category_name
        chosen = numpy.random.choice(a=range(_genome_size), size=lst.size(),
                                     replace=False)
        for n in chosen:
            ent = self.get_or_create_entity(n)
            new_list.append(ent)
        return new_list

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


def random_data_matching_code_string(code_string, random_source_len):
    """Given a coded string such as that generated by the
    CrossValidation.code_string() routine, return a list of strings that can
    subsequently be used to generate a set of lists identical in pattern to
    the one supplied."""
    logger.debug(
        "Generating a set of random lists from string '%s' and a "
        "genome containing '%d' entities" % (code_string, random_source_len))
    string_list = []
    cat_counter = 1
    list_counter = 1
    for category_string in code_string.split("|"):
        category_name = "category" + str(cat_counter)
        for list_string in category_string.split('.'):
            list_name = "list" + str(list_counter)
            match = re.search("^(\\d+)([ur])$", list_string, re.M)
            length = int(match.groups()[0])
            ranked = 'RANKED' if match.groups()[1] == 'r' else 'UNRANKED'
            chosen = numpy.random.choice(random_source_len, length, False)
            string_list.append(
                '\t'.join(
                    [category_name, list_name, ranked, 'reserved']
                    + [str(x) for x in chosen]
                )
            )
            list_counter += 1
        cat_counter += 1
    return string_list


def build_cross_validation(lines, entity_list_builder, stability,
                           max_iterations,twiddle_method=None):
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
                                       twiddle_method)
    return cross_validation
