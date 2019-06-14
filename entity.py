"""
Code relating to the creation and management of Entities
"""


class Entity:
    """Represent an entity (e.g. a gene)."""

    def __init__(self, name):
        """Build a new Entity object."""
        assert name
        self.name = name
        self.score = 1
        self.twiddled_score = 1
        self.lists = []
        self.__weights = {}
        self.__category_winners = {}

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

    def calculate_new_score(self, correction_method = None):
        """Calculate the new score for this Entity"""
        # Set up some accumulators and a pair of dictionaries for tracking
        # purposes
        new_score = 0
        new_twiddled_score = 0
        category_scores = {}
        category_twiddled_scores = {}

        # For each list in turn...
        for lst in self.lists:
            # Grab the weight and the twiddled weight for this entity on
            # that list
            lst_weight = lst.get_weight_for_entity(self)
            lst_twiddled_weight = lst.get_weight_for_entity(self,
                                                            correction_method)
            # TODO - decide if we need to deal with un-twiddled weights at all
            self.__weights[lst] = lst_twiddled_weight

            # If we've already got a score for this category then check to
            # see if this score is better. If it is, then forget the
            # previous value and use this one
            if lst.category in category_scores:
                if lst_weight > category_scores[lst.category]:

                    new_score -= category_scores[lst.category]
                    new_twiddled_score -= category_twiddled_scores[
                        lst.category]

                    category_scores[lst.category] = lst_weight
                    category_twiddled_scores[lst.category] = lst_twiddled_weight

                    new_score += lst_weight
                    new_twiddled_score += lst_twiddled_weight

                    self.__category_winners[lst.category] = lst
            else:
                category_scores[lst.category] = lst_weight
                category_twiddled_scores[lst.category] = lst_twiddled_weight

                new_score += lst_weight
                new_twiddled_score += lst_twiddled_weight
                
                self.__category_winners[lst.category] = lst
        self.score = new_score
        self.twiddled_score = new_twiddled_score

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
