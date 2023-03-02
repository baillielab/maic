from maic.cross_validation import CrossValidation
from maic.io.genescores_dumper import IterationAwareGeneScoresDumper

class CrossValidationDumper:
    dumper: IterationAwareGeneScoresDumper
    def __init__(self, dumper: IterationAwareGeneScoresDumper = ...) -> None: ...
    def do_callback(self, cross_validation: CrossValidation = ..., iteration: int = ...): ...
