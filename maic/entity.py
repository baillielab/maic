"""
Code relating to the creation and management of Entities
"""
from .entitylist import adjusted_weight
from .constants import T_METHOD_NONE


class Entity:
    """Represent an entity (e.g. a gene)."""

    def __init__(self, name):
        """Build a new Entity object."""
        assert name
        self.name = name
        self.score = 1
        self.lists = []
        self.__weights = {}
        self.__category_winners = {}
        self.adjusted_scores = {}

    def transformed_score(self, method=T_METHOD_NONE):
        """Return the transformed score for the requested transform method.
        If no matching score is found then return zero"""
        transformed_score = 0
        if method in self.adjusted_scores:
            transformed_score = self.adjusted_scores.get(method)
        return transformed_score

    def as_dict_for_json(self):
        """Convert the relevant fields to a dictionary suitable for dumping
        as JSON"""
        return dict(name=self.name, adjusted_scores=self.adjusted_scores,
                    score=self.score)

    def note_list(self, entity_list):
        """
        Add the supplied list to our list of lists if it wasn't already in
        there.
        """
        if entity_list not in self.lists:
            self.lists.append(entity_list)
            self.__weights[entity_list] = 0.0

    def forget_list(self, entity_list):
        if entity_list in self.lists:
            self.lists.remove(entity_list)
            del self.__weights[entity_list]

    def calculate_final_corrected_scores(self, methods=None):
        """Having reached completion, we can now calculate the corrected or
        adjusted scores based on a number of options"""

        # KJB, BW, AL agreed on 26th April 2019 that it is correct to
        # calculate a new score _after_ the weights have converged
        if methods is None:
            methods = []
        self.calculate_new_score()
        adjusted_weights = {}

        # Set up a data structure to grab back all the weights, sorted by
        # list category
        for method in methods:
            adjusted_weights[method] = {}
            for lst in self.lists:
                if lst.category not in adjusted_weights[method]:
                    adjusted_weights[method][lst.category] = []

        # Get the local (list-specific) weights
        adjusted_scores = {}
        for lst in self.lists:
            lst_weights = lst.get_final_weights_for_entity(self, methods)
            for method in lst_weights:
                adjusted_weights[method][lst.category].append(
                    lst_weights[method])

        # And then sum the maximum adjusted weights in each category to give
        # a final score
        for method in methods:
            adjusted_scores[method.name] = self.sum_max_weights_per_category(
                adjusted_weights[method])

        adjusted_scores[T_METHOD_NONE] = self.score

        self.adjusted_scores = adjusted_scores

    @staticmethod
    def sum_max_weights_per_category(weights):
        """Calculate the sum of the highest value in each of the categories
        in the weights dictionary"""
        sum_of_weights = 0.0
        for category in weights:
            sum_of_weights += max(weights[category])
        return sum_of_weights

    def calculate_new_score(self):
        """Calculate the new score for this Entity"""
        # Set up some accumulators and a pair of dictionaries for tracking
        # purposes
        new_score = 0
        category_scores = {}

        # For each list in turn...
        for lst in self.lists:
            # Grab the weight and the transformed weight for this entity on
            # that list
            lst_weight = lst.get_weight_for_entity(self)
            self.__weights[lst] = lst_weight

            # If we've already got a score for this category then check to
            # see if this score is better. If it is, then forget the
            # previous value and use this one
            if lst.category in category_scores:
                if lst_weight > category_scores[lst.category]:
                    new_score -= category_scores[lst.category]
                    category_scores[lst.category] = lst_weight
                    new_score += lst_weight
                    self.__category_winners[lst.category] = lst
            else:
                category_scores[lst.category] = lst_weight
                new_score += lst_weight
                self.__category_winners[lst.category] = lst
        self.score = new_score

    def score_from_list(self, entity_list):
        """Report the contribution of the given list to the current score"""
        return_value = 0.0
        if entity_list in self.lists:
            category = entity_list.category
            if category in self.__category_winners:
                if self.__category_winners[entity_list.category] == \
                        entity_list:
                    return_value = self.__weights[entity_list]
        return return_value

    def raw_score_from_list(self, entity_list):
        """Report the score that this entity would receive from this list
        regardless of whether or not this list is the winner in its category"""
        return_value = 0.0
        if entity_list in self.lists:
            return_value = self.__weights[entity_list]
        return return_value

    def winning_lists_by_category(self):
        """Return a dictionary of category->list pairs indicating the
        winning lists for each category"""
        return self.__category_winners

    def reset(self):
        """Reset an Entity so that we can re-run an analysis"""
        self.score = 1
        self.__category_winners = {}
        for lst in self.__weights:
            self.__weights[lst] = 0.0
