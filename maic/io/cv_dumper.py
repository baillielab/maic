from maic.io.genescores_dumper import IterationAwareGeneScoresDumper


class CrossValidationDumper(object):

    def __init__(self, dumper=None):
        super(CrossValidationDumper, self).__init__()
        self.dumper = dumper

    def do_callback(self, cross_validation=None, iteration=None):
        if cross_validation == self.dumper.cross_validation:
            self.dumper.iteration = iteration
            self.dumper.dump()
