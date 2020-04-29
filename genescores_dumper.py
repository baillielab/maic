import io
import sys

from constants import T_METHOD_NONE


# TODO - rewrite this object to handle TransformMethods rather than separate
#  methods

class GeneScoresDumper(object):

    def __init__(self, cross_validation, output_folder=None):
        """Create a GeneScoresDumper object for the given CrossValidation
        analysis"""
        self.cross_validation = cross_validation
        self.output_folder = output_folder

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

    def build_file_and_method_name(self, method=T_METHOD_NONE, baseline=None):
        """Given a method and a baseline, return an object
        containing an appropriate filename and method name. The former is
        used to write data out, the latter is used to extract the scores data
        from the entities within this analysis"""
        ret_val = FileAndMethodName()
        if method == T_METHOD_NONE:
            ret_val.filename = "maic_raw"
            ret_val.methodname = "no_transform"
        else:
            if baseline:
                ret_val.methodname = "{}-{}".format(baseline, method.name)
            else:
                ret_val.methodname = method.name
            ret_val.filename = ret_val.methodname
        return ret_val

    def dump(self, method=T_METHOD_NONE, baseline=None):
        """Actually do the GeneScoresDump into the supplied stream"""
        famn = self.build_file_and_method_name(method, baseline)
        # if there's a folder, create an output file stream otherwise write
        # a header and the data to stdout
        out_stream = sys.stdout
        if self.output_folder:
            out_stream = io.open(
                "{}{}.txt".format(self.output_folder, famn.filename), 'w+')
        else:
            out_stream.writelines("-------- {} ---------".format(famn.filename))

        lists = self.lists_in_category_order()
        out_stream.writelines('\t'.join(
            ['gene'] + [lst.name for lst in lists] + [
                'maic_score'] + self.extra_headers()) + '\n')
        for entity in self.entities_in_descending_score_order(
                method=famn.methodname):
            out_columns = [entity.name]
            for lst in lists:
                score = max(0.0, self.score_for_entity_from_list(entity, lst))
                out_columns.append(str(score))
            out_columns.append(
                str(entity.transformed_score(method=famn.methodname)))
            out_columns += self.additional_column_data(entity)
            out_stream.writelines('\t'.join(out_columns) + '\n')

    def entities_in_descending_score_order(self, method=T_METHOD_NONE):
        return sorted(self.cross_validation.entities,
                      key=lambda x: x.transformed_score(method=method),
                      reverse=True)

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


class IterationAwareGeneScoresDumper(AllScoresGeneScoresDumper):
    """A version of the GeneScoresDumper object that knows about which
    iteration it is being called from (using the CrossValidation callback
    mechanism"""

    def __init__(self, cross_validation, output_folder=None):
        super(IterationAwareGeneScoresDumper, self).__init__(
            cross_validation=cross_validation,
            output_folder=output_folder
        )
        self.iteration = 0

    def build_file_and_method_name(self, method=T_METHOD_NONE, baseline=None):
        initial = super(IterationAwareGeneScoresDumper,
                        self).build_file_and_method_name(method=method,
                                                         baseline=baseline)
        initial.filename = "{}-{:03d}".format(initial.filename, self.iteration)
        return initial


class FileAndMethodName(object):

    def __init__(self):
        self.filename = ""
        self.methodname = ""
