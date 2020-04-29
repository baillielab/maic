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

logging.basicConfig()
logger = logging.getLogger(__name__)

# Value we use to buold a fake list of distributed weights if our ranked list
# fails to fit a function successfully
FAILED_RANKED_LIST_DESCENT_STEP = 0.00000001


class EntityList(object):
    """Represent a list of Entity objects"""

    __list_category_counter = 0
    lock = Lock()

    def __init__(self):
        """Build a default EntityList object."""
        self.__list = []
        self.__seen = {}
        self.__entity_indexes_one_based = {}
        self.__total_entity_weight = 0.0
        self.__entity_count_minus_one = 1
        self.is_ranked = False
        self.weight = 1
        self.delta = None
        self.category_name = ""  # side-effect sets the category as well
        self.name = ""
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

    def append(self, entity):
        """Add the Entity to the end of the list"""
        if entity not in self.__seen:  # quicker than scanning the list
            self.__list.append(entity)
            self.__seen[entity] = 1
            entity.note_list(self)
            self.__entity_indexes_one_based[entity] = len(self.__list)

    def tell_entities_to_forget(self):
        for entity in self.__list:
            entity.forget_list(self)

    def tell_entities_to_remember(self):
        for entity in self.__list:
            entity.note_list(self)

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
            super(EntityList, self).__setattr__('category', category)
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

    def get_corrected_list_weight(self, score_to_ignore):
        """
        Calculate a corrected weight for this list as if the score_to_ignore
        were not in the list.

        We assume that the weight has already been calculated.

        NOTE: This will fail with an Exception on an empty list
        """
        return sqrt((self.__total_entity_weight - score_to_ignore) /
                    self.__entity_count_minus_one)

    def get_final_weights_for_entity(self, entity, correction_options):
        """Calculate all the requested corrected weights for the given
        entity and return them in a dictionary"""
        weights = {}
        if entity and entity in self.__seen:
            index = self.__entity_indexes_one_based[entity]
            initial = self._weight_function(index)

            for correction in correction_options:
                weighted_value = adjusted_weight(initial, self.base_score_mean,
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

    def code_string(self):
        ranked_string = "r" if self.is_ranked else "u"
        return str(len(self)) + ranked_string

    def size(self):
        return len(self.__list)

    def blank_copy(self):
        """Return a new blank EntityList"""
        return EntityList()

    def get_entities(self):
        return self.__list

    def set_baseline(self, base_score_mean, base_score_stdev):
        self.base_score_mean = base_score_mean
        self.base_score_stdev = base_score_stdev

    def _correct_fitted_weights(self):
        """Adjust the values in the fitted weights list to maintain the
        average weight contribution of all lists in line with that of an
        unranked list"""
        #self.weights_list = np.true_divide(self.weights_list, self.ratio)
        pass


class KnnEntityList(EntityList):

    def _fit_curve_to_entity_scores(self):
        y_vector = self.get_truncated_weights_list()
        knn = neighbors.KNeighborsRegressor(n_neighbors=3, weights='distance')
        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x_vector = x.reshape(-1, 1)
        knn.fit(x_vector, y_vector)
        weights = knn.predict(x_vector)
        weights = list(weights)
        self.weights_list = weights
        self.ratio = np.average(weights) / self.weight

    def _weight_function(self, index):
        return_value = 1
        if len(self.weights_list) == self.size():
            return_value = self.weights_list[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('KNN Entity List returned weight 1 because we '
                         'had no parameters')

        return return_value

    def blank_copy(self):
        """Return a new blank EntityList"""
        return KnnEntityList()


class PolynomialEntityList(EntityList):

    def _fit_curve_to_entity_scores(self):
        """Do the Polynomial-specific curve fitting."""
        y_vector = self.get_truncated_weights_list()
        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x = x.reshape(-1, 1)
        model = make_pipeline(PolynomialFeatures(2), Ridge())
        model.fit(x, y_vector)
        weights = model.predict(x)
        self.weights_list = weights
        self.ratio = np.average(weights) / self.weight

    def _weight_function(self, index):
        """Calculate the Polynomial-specific adjusted weight for entry at
        index."""
        return_value = 1
        if len(self.weights_list) == self.size():
            return_value = self.weights_list[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('Polynomial Entity List returned weight 1 because we '
                         'had no parameters')
        return return_value

    def blank_copy(self):
        """Return a new blank EntityList"""
        return PolynomialEntityList()


class SvrEntityList(EntityList):
    """EntityList that uses a Support Vector Regression with a Radial
    Basis Function to model and distribute weights"""

    def _fit_curve_to_entity_scores(self):
        y_vector = self.get_truncated_weights_list()
        clf = SVR(kernel='rbf', C=1.0, epsilon=0.2)
        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x_vector = x.reshape(-1, 1)
        clf.fit(x_vector, y_vector)
        weights = list(clf.predict(x_vector))
        self.weights_list = weights
        self.ratio = np.average(weights) / self.weight

    def _weight_function(self, index):

        return_value = 1
        if len(self.weights_list) == self.size():
            return_value = self.weights_list[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('SVR Entity List returned weight 1 because we '
                         'had no parameters')
        return return_value

    def blank_copy(self):
        """Return a new blank EntityList"""
        return SvrEntityList()


class ExponentialEntityList(EntityList):

    def __init__(self):
        super(ExponentialEntityList, self).__init__()
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

    def blank_copy(self):
        """Return a new blank EntityList"""
        return ExponentialEntityList()


def adjusted_weight(initial, baseline_mean, baseline_stdev, transformer,
                    scaler):
    """
    Correct an initial weight/score as per specified transform and scale
    methods (applied in that order)
    """
    transformed_score = transformer.transform(initial, baseline_mean)
    scaled_score = scaler.scale(transformed_score, baseline_stdev)

    return scaled_score
