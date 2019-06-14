import logging
import re
from math import pow
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
        self.base_score_mean = 0.0 # safe default values
        self.base_score_stdev = 1.0
        self.base_weight_mean = 0.0

    def reset(self):
        """Reset a list to a pre-calculation state"""
        self.__total_entity_weight = 0.0
        self.weight = 1
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
        return sqrt((
                            self.__total_entity_weight - score_to_ignore) /
                    self.__entity_count_minus_one)

    def get_weight_for_entity(self, entity, correction=None):
        """
        Return the weight that this list provides to the given Entity
        :param entity: the Entity in question
        :param correction: the baseline correction method to be applied
        :return: the weight to be used by that Entity

        NOTE: correction methods are only valid once the analysis is complete
        """
        return_value = 0.0
        if entity and entity in self.__seen:
            index = self.__entity_indexes_one_based[entity]
            return_value = self._weight_function(index)
        if correction is not None and correction != 'none':
            if correction == "mean":
                return_value = max(0.0, return_value - self.base_score_mean)
            elif correction == "z-transform":
                return_value = max(0.0, (
                        return_value - self.base_score_mean) /
                                   self.base_score_stdev)
            elif correction == ("onebelow_z"):
                baseline = self.base_score_mean - self.base_score_stdev
                return_value = max(0.0,
                                   return_value - baseline /
                                   self.base_score_stdev)
            #----------
            elif correction.startswith("pow_"):
                exponent = float(correction.replace("pow_", ""))
                return_value = max(0.0, return_value - self.base_score_mean)
                if return_value > 0:
                    return_value = pow(return_value, exponent)
            elif correction.startswith("onebelowpow_"):
                exponent = float(correction.replace("onebelowpow_", ""))
                baseline = self.base_score_mean - self.base_score_stdev
                return_value = max(0.0, return_value - baseline)
                if return_value > 0:
                    return_value = pow(return_value, exponent)
            elif correction.startswith("scale_"):
                divisor = float(correction.replace("scale_", ""))
                return_value = max(0.0,
                                   return_value - self.base_score_mean /
                                   divisor)
            elif correction.startswith("onebelowscale_"):
                divisor = float(correction.replace("onebelowscale_", ""))
                baseline = self.base_score_mean - self.base_score_stdev
                return_value = max(0.0,
                                   return_value - baseline /
                                   divisor)
            #----------
            elif correction.startswith("nomean_pow_"):
                exponent = float(correction.replace("nomean_pow_", ""))
                return_value = max(0.0, return_value)
                if return_value > 0:
                    return_value = pow(return_value, exponent)
            elif correction.startswith("nomean_onebelowpow_"):
                exponent = float(correction.replace("nomean_onebelowpow_", ""))
                baseline = - self.base_score_stdev
                return_value = max(0.0, return_value - baseline)
                if return_value > 0:
                    return_value = pow(return_value, exponent)
            elif correction.startswith("nomean_scale_"):
                divisor = float(correction.replace("nomean_scale_", ""))
                return_value = max(0.0,
                                   return_value /
                                   divisor)
            elif correction.startswith("nomean_onebelowscale_"):
                divisor = float(correction.replace("nomean_onebelowscale_", ""))
                baseline =  - self.base_score_stdev
                return_value = max(0.0,
                                   return_value - baseline /
                                   divisor)

            # other correction methods go here

            else:
                logger.warning(
                    "Did not recognise the correction method '%s\." %
                    correction)

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

    def set_baseline(self, base_score_mean, base_score_stdev,
                     base_weight_mean):
        self.base_score_mean = base_score_mean
        self.base_score_stdev = base_score_stdev
        self.base_weight_mean = base_weight_mean


class KnnEntityList(EntityList):

    def _fit_curve_to_entity_scores(self):
        y_vector = []
        running_total = 0.0
        counter = 1
        for entity in self:
            running_total += entity.score
            y_vector.append(sqrt(running_total / counter))
            counter += 1
        knn = neighbors.KNeighborsRegressor(n_neighbors=3, weights='distance')
        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x_vector = x.reshape(-1, 1)
        knn.fit(x_vector, y_vector)
        weights = knn.predict(x_vector)
        weights = list(weights)
        weights = sorted(weights, reverse=True)
        self.fit_parameters = weights

    def _weight_function(self, index):
        return_value = 1
        if hasattr(self, 'fit_parameters'):
            weights = self.fit_parameters
            return_value = weights[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('KNN Entity List returned weight 1 because we '
                         'had no parameters')

        return return_value

    def reset(self):
        """Reset a KnnEntityList object after calculations"""
        if hasattr(self, 'fit_parameters'):
            del self.fit_parameters
        super(KnnEntityList, self).reset()

    def blank_copy(self):
        """Return a new blank EntityList"""
        return KnnEntityList()


class PolynomialEntityList(EntityList):

    def _fit_curve_to_entity_scores(self):
        """Do the Polynomial-specific curve fitting."""
        y_vector = []
        running_total = 0.0
        counter = 1
        for entity in self:
            running_total += entity.score
            y_vector.append(sqrt(running_total / counter))
            counter += 1

        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x = x.reshape(-1, 1)
        model = make_pipeline(PolynomialFeatures(2), Ridge())
        model.fit(x, y_vector)
        weights = model.predict(x)
        weights = sorted(weights, reverse=True)
        self.fit_parameters = weights

    def _weight_function(self, index):
        """Calculate the Polynomial-specific adjusted weight for entry at
        index."""
        return_val = 1
        if hasattr(self, 'fit_parameters'):
            weights = self.fit_parameters
            return_val = weights[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('Polynomial Entity List returned weight 1 because we '
                         'had no parameters')
        return return_val

    def reset(self):
        """Reset a PolynomialEntityList object after calculations"""
        if hasattr(self, 'fit_parameters'):
            del self.fit_parameters
        super(PolynomialEntityList, self).reset()

    def blank_copy(self):
        """Return a new blank EntityList"""
        return PolynomialEntityList()


class SvrEntityList(EntityList):
    """EntityList that uses a Support Vector Regression with a Radial
    Basis Function to model and distribute weights"""

    def _fit_curve_to_entity_scores(self):
        y_vector = []
        running_total = 0.0
        counter = 1
        for entity in self:
            running_total += entity.score
            y_vector.append(sqrt(running_total / counter))
            counter += 1
        clf = SVR(kernel='rbf', C=1.0, epsilon=0.2)
        x = list(range(1, len(y_vector) + 1, 1))
        x = np.asanyarray(x)
        y_vector = np.asanyarray(y_vector)
        x_vector = x.reshape(-1, 1)
        clf.fit(x_vector, y_vector)
        weights = list(clf.predict(x_vector))
        weights.sort(reverse=True)
        self.fit_parameters = weights

    def _weight_function(self, index):

        return_value = 1
        if hasattr(self, 'fit_parameters'):
            weights = self.fit_parameters
            return_value = weights[index - 1]
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('SVR Entity List returned weight 1 because we '
                         'had no parameters')
        return return_value

    def reset(self):
        """Reset a SvrEntityList object after calculations"""
        if hasattr(self, 'fit_parameters'):
            del self.fit_parameters
        super(SvrEntityList, self).reset()

    def blank_copy(self):
        """Return a new blank EntityList"""
        return SvrEntityList()


class ExponentialEntityList(EntityList):

    def _fit_curve_to_entity_scores(self):
        """Do the Exponential-specific curve fitting."""

        def func(x, a, b, c):
            return a * np.exp(-b * x) + c

        y_vector = []
        running_total = 0.0
        counter = 1
        for entity in self:
            running_total += entity.score
            y_vector.append(sqrt(running_total / counter))
            counter += 1

        x_vector = list(range(1, len(y_vector) + 1, 1))

        y_vector = np.asanyarray(y_vector)
        x_vector = np.asanyarray(x_vector)

        popt, pcov = curve_fit(func, x_vector, y_vector,
                               bounds=(0, [20, 10, .01]))
        self.fit_parameters = popt
        self.fit_average = np.mean(y_vector)

    def _weight_function(self, index):
        """Calculate the Exponential-specific adjusted weight for entry at
        index."""
        return_value = 1
        if hasattr(self, 'fit_parameters'):
            a, b, c = self.fit_parameters
            return_value = (a * np.exp(-b * index) + c)  # / self.fit_average
            logger.debug(
                ' '.join((str(self.name), str(index), str(self.weight))))
        else:
            logger.debug('ExponentialEntityList returned weight 1 because we '
                         'had no parameters')
        return return_value

    def reset(self):
        """Reset an ExponentialEntityList object after calculations"""
        if hasattr(self, 'fit_parameters'):
            del self.fit_parameters
        if hasattr(self, 'fit_average'):
            del self.fit_average
        super(ExponentialEntityList, self).reset()

    def blank_copy(self):
        """Return a new blank EntityList"""
        return ExponentialEntityList()
