class GeneScoresDumper(object):

    def __init__(self, cross_validation, baseline=None):
        """Create a GeneScoresDumper object for the given CrossValidation
        analysis"""
        self.cross_validation = cross_validation
        self.baseline = baseline

    def lists_in_category_order(self):
        """Return a list of EntityList objects from the CrossValidation
        sorted by category and then by name"""
        categories = {}
        for lst in self.cross_validation.entity_lists:
            if lst.category not in categories:
                categories[lst.category] = []
            categories[lst.category].append(lst)
        lists = []
        for category in sorted(categories.keys()):
            categories[category].sort(key=lambda x: x.name.lower())
            for lst in categories[category]:
                lists.append(lst)
        return lists

    def dump(self, out_stream):
        """Actually do the GeneScoresDump into the supplied stream"""
        # get the baseline values for calculating z-scores/z-transformations
        # If no baseline is supplied then (0.0,1.0) will leave everything as it
        mean = 0.0
        stdev = 1.0
        if self.baseline is not None:
            mean = self.baseline.base_score
            stdev = self.baseline.base_stdev

        lists = self.lists_in_category_order()
        out_stream.writelines('\t'.join(
            ['gene'] + [lst.name for lst in lists] + [
                'maic_score'] + self.extra_headers()) + '\n')
        for entity in self.entities_in_descending_score_order():
            out_columns = [entity.name]
            for lst in lists:
                score = max(0.0,
                            (self.score_for_entity_from_list(entity, lst)
                             - mean) / stdev)
                out_columns.append(str(score))
            out_columns.append(str(entity.twiddled_score))
            out_columns += self.additional_column_data(entity)
            out_stream.writelines('\t'.join(out_columns) + '\n')

    def entities_in_descending_score_order(self):
        return sorted(self.cross_validation.entities,
                      key=lambda x: x.twiddled_score, reverse=True)

    def extra_headers(self):
        return []

    def score_for_entity_from_list(self, entity, lst):
        return entity.score_from_list(lst)

    def additional_column_data(self, entity):
        return []


class AllScoresGeneScoresDumper(GeneScoresDumper):

    def extra_headers(self):
        return ['contributors']

    def score_for_entity_from_list(self, entity, lst):
        return entity.raw_score_from_list(lst)

    def additional_column_data(self, entity):
        return_value_list = []
        category_winners = entity.winning_lists_by_category()
        for category in category_winners:
            lst = category_winners[category]
            return_value_list.append("%s: %s" % (category, lst.name))
        return [", ".join(return_value_list)]
