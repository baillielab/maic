from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maic.io.genescores_dumper import IterationAwareGeneScoresDumper
    from maic.cross_validation import CrossValidation

class CrossValidationDumper(object):

    def __init__(self, dumper:IterationAwareGeneScoresDumper=None):
        super(CrossValidationDumper, self).__init__()
        self.dumper = dumper

    def do_callback(self, cross_validation:CrossValidation=None, iteration:int=None):
        if cross_validation == self.dumper.cross_validation:
            self.dumper.iteration = iteration
            self.dumper.dump()
