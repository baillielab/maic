import logging
import re
from math import sqrt
from threading import Lock

import numpy as np
from scipy.optimize import curve_fit
from sklearn import neighbors
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR

from typing import Sequence, MutableSequence
from maic.types import Corrector, Transformer, Scaler

from .models import EntityListModel
from .entity import Entity



logging.basicConfig()
logger = logging.getLogger(__name__)

# Value we use to buold a fake list of distributed weights if our ranked list
# fails to fit a function successfully
FAILED_RANKED_LIST_DESCENT_STEP = 0.00000001


class EntityList(object):
    """Represent a list of Entity objects"""

    from sys import maxsize
    @staticmethod
    def frommodel(elm: EntityListModel, *args, entities: dict[str,Entity] = {}, limit:int=maxsize) -> 'EntityList':
        self = EntityList(elm.name, elm.category, elm.is_ranked)

        for entity_name in elm.entities[:limit]:
            e = entities.setdefault(entity_name, Entity(entity_name))
            self.append(e)
        
        if len(elm.entities) > limit:
            logger.warn(f"Some data in list '{self.name}' was ignored due to a limit on list lengths ({limit}). {len(elm.entities) - limit} entities were skipped.")
        
        return self

    __list_category_counter: int = 0
    lock: Lock = Lock()

    # redundant - only referenced in redundant method EntityList.get_final_weights_for_entity() (and testing)
    @staticmethod
    def adjusted_weight(initial: float, baseline_mean:float, baseline_stdev:float, transformer: Transformer, scaler: Scaler):
        """
        Correct an initial weight/score as per specified transform and scale
        methods (applied in that order)
        """
        transformed_score = transformer.transform(initial, baseline_mean)
        scaled_score = scaler.scale(transformed_score, baseline_stdev)

        return scaled_score

    def __init__(self, name:str="", category:str="", is_ranked:bool=False):
        """Build a default EntityList object."""
        self.__list: MutableSequence[Entity] = []
        self.__seen: dict[str,Entity] = {}
        self.__entity_indexes_one_based: dict[Entity, int] = {}
        self.__total_entity_weight = 0.0
        self.__entity_count_minus_one = 1
        self.is_ranked = is_ranked
        self.weight = 1
        self.delta = None
        self.category_name = category  # side-effect sets the category as well
        self.name = name
        self.base_score_mean = 0.0  # safe default values
        self.base_score_stdev = 1.0
        self.need_local_baseline_base_score_mean = 0.0  # safe default values
        self.weights_list = [self.weight]
        self.ratio = 1

    def reset(self):
        """Reset a list to a pre-calculation state"""
        self.__total_entity_weight = 0.0
        self.weight = 1
        self.weights_list = [self.weight]
        self.ratio = 1
        self.delta = None
        for lst in self.__list:
            lst.reset()

    def append(self, entity: Entity):
        """Add the Entity to the end of the list"""
        if entity not in self.__seen:  # quicker than scanning the list
            self.__list.append(entity)
            self.__seen[entity] = 1
            entity.note_list(self)
            self.__entity_indexes_one_based[entity] = len(self.__list)

    # unused
    def tell_entities_to_forget(self):
        for entity in self.__list:
            entity.forget_list(self)

    # unused
    def tell_entities_to_remember(self):
        for entity in self.__list:
            entity.note_list(self)

    # duplicate: same method appears below with different definition!
    def get_entities(self):
        return self.__seen

    def get_truncated_weights_list(self):
        y_vector = []
        running_total = 0.0
        counter = 1
        for entity in self:
            running_total += entity.score
            y_vector.append(sqrt(running_total / counter))
            counter += 1
        return y_vector

    @property
    def category(self) -> str:
        return self._category

    def __setattr__(self, key, value):
        """
        Intercept attribute setting and special case where required.

        Setting category_name also sets category as a side-effect.
        """
        if key == 'name':
            value = value.strip()
        if key == 'category_name':
            value = value.strip()
            if value:
                category = re.sub(" +", "-", value.upper())
            else:
                EntityList.lock.acquire()
                EntityList.__list_category_counter += 1
                category = "Unknown-{:03d}".format(
                    EntityList.__list_category_counter)
                EntityList.lock.release()
            super(EntityList, self).__setattr__('_category', category)
        elif key == 'category':
            raise AttributeError("Can't set 'category' attribute directly")
        super(EntityList, self).__setattr__(key, value)

    def __len__(self):
        """Report the length of the list of Entity objects"""
        return len(self.__list)

    def __iter__(self):
        """Make the EntityList iterable."""
        return self.__list.__iter__()

    def calculate_new_weight(self):
        """
        Calculate the new weight of this EntityList based on the Entities it
        contains.
        Record and return the change in list weight (delta) as a side-effect
        """
        old_weight = self.weight
        self.__total_entity_weight = 0.0
        if len(self.__list):
            for entity in self.__list:
                self.__total_entity_weight += entity.score
            average = self.__total_entity_weight / len(self.__list)
            self.weight = sqrt(average)
        else:
            self.weight = 0.0
        self.delta = self.weight - old_weight
        self.__entity_count_minus_one = max(1, len(self.__list) - 1)
        self._fit_curve_to_entity_scores()
        self._correct_fitted_weights()
        return self.delta

    def _fit_curve_to_entity_scores(self):
        """
        Fit a curve to the Entity scores within this List
        :return:
        """
        pass

    # unused - used only in testing
    def get_corrected_list_weight(self, score_to_ignore):
        """
        Calculate a corrected weight for this list as if the score_to_ignore
        were not in the list.

        We assume that the weight has already been calculated.

        NOTE: This will fail with an Exception on an empty list
        """
        return sqrt((self.__total_entity_weight - score_to_ignore) /
                    self.__entity_count_minus_one)

    # redundant - only referenced in redundant method Entity.calculate_final_corrected_scores()
    def get_final_weights_for_entity(self, entity: Entity, correction_options: Sequence[Corrector]) -> dict[Corrector, float]:
        """Calculate all the requested corrected weights for the given
        entity and return them in a dictionary"""
        weights = {}
        if entity and entity in self.__seen:
            index = self.__entity_indexes_one_based[entity]
            initial = self._weight_function(index)

            for correction in correction_options:
                weighted_value = EntityList.adjusted_weight(initial, self.base_score_mean,
                                                 self.base_score_stdev,
                                                 correction.transformer,
                                                 correction.scaler)
                weights[correction] = weighted_value

        return weights

    def get_weight_for_entity(self, entity):
        """
        Return the weight that this list provides to the given Entity
        :param entity: the Entity in question
        :return: the weight to be used by that Entity

        NOTE: correction methods are only valid once the analysis is complete
        """
        return_value = 0.0
        if entity and entity in self.__seen:
            index = self.__entity_indexes_one_based[entity]
            return_value = self._weight_function(index)
        return return_value

    def _weight_function(self, index):
        """
        Given the index number (one-based) of an Entity within this list,
        return the adjusted weight for that Entity from this list. The default
        implementation just returns the list weight unadjusted.
        :param index:
        :return:
        """
        return self.weight

    # redundant - only called in an unused method
    def code_string(self):
        ranked_string = "r" if self.is_ranked else "u"
        return str(len(self)) + ranked_string

    def size(self):
        return len(self.__list)

    # unused
    def blank_copy(self):
        """Return a new blank EntityList"""
        return EntityList()

    # duplicate - see above:
    def get_entities(self):
        return self.__list

    # unused
    def set_baseline(self, base_score_mean, base_score_stdev):
        self.base_score_mean = base_score_mean
        self.base_score_stdev = base_score_stdev

    # redundant - this method is called but it does nothing (body has been commented out).
    def _correct_fitted_weights(self):
        """Adjust the values in the fitted weights list to maintain the
        average weight contribution of all lists in line with that of an
        unranked list"""
        #self.weights_list = np.true_divide(self.weights_list, self.ratio)
        pass


class ExponentialEntityList(EntityList):
    from sys import maxsize
    @staticmethod
    def frommodel(elm: EntityListModel, *args, entities: dict[str,Entity] = {}, limit:int=maxsize) -> 'ExponentialEntityList':
        self = ExponentialEntityList(elm.name, elm.category, elm.is_ranked)

        for entity_name in elm.entities[:limit]:
            e = entities.setdefault(entity_name, Entity(entity_name))
            self.append(e)
        
        if len(elm.entities) > limit:
            logger.warn(f"Some data in list '{self.name}' was ignored due to a limit on list lengths ({limit}). {len(elm.entities) - limit} entities were skipped.")
        
        return self

    def __init__(self, name:str="", category:str="", is_ranked:bool=False):
        super().__init__(name, category, is_ranked)
        self.fit_parameters = None

    def _fit_curve_to_entity_scores(self):
        """Do the Exponential-specific curve fitting."""

        def func(x, a, b, c, d):
            return a * np.exp(-b * x) - c * x + d

        y_vector = self.get_truncated_weights_list()

        x_vector = list(range(1, len(y_vector) + 1, 1))

        y_vector = np.asanyarray(y_vector)
        x_vector = np.asanyarray(x_vector)
        weights = []
        try:
            optimal_parameters, covariance = curve_fit(
                func, x_vector, y_vector,
                # starting values to speed it up
                p0=[3, 0.01, 0.0001, self.weight],
                # variance scales linearly with number of entities
                sigma=[self.weight*(len(x_vector)-i+1)/len(x_vector) for i in x_vector],
                bounds = ([0, 0, 0.00000001, 0], [np.inf, np.inf, np.inf, np.inf]))
            #print (self.name, self.weight, optimal_parameters)
            self.fit_parameters = optimal_parameters
            a, b, c, d = self.fit_parameters
            for x in x_vector:
                weights.append(a * np.exp(-b * x) - c * x + d)
            self.weights_list = weights
            self.ratio = np.average(weights) / self.weight
        except RuntimeError as error:
            logger.warning("An error occured when trying to fit a "
                           "function to distribute weights for "
                           "list {}. The error was '{}'".format(self.name,
                                                                error))
            self.fit_parameters = [0, 0, 0, 0]
            entity_count = len(self)
            base = self.weight + (
                    (FAILED_RANKED_LIST_DESCENT_STEP * entity_count) / 2.0)
            for x in range(entity_count):
                weights.append(
                    base - (x * FAILED_RANKED_LIST_DESCENT_STEP))
            self.weights_list = weights
            self.ratio = 1

    def _weight_function(self, index):
        """Return the precalculated and adjusted Exponential-specific adjusted
        weight for entry at
        index."""
        return_value = 1
        if len(self.weights_list) == self.size():
            return_value = self.weights_list[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('ExponentialEntityList returned weight 1 because we '
                         'had no parameters')
        return return_value

    def reset(self):
        super(ExponentialEntityList, self).reset()
        self.fit_parameters = None

    # unused
    def blank_copy(self):
        """Return a new blank EntityList"""
        return ExponentialEntityList()
