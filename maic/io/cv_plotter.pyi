from maic.cross_validation import CrossValidation
from math import sqrt as sqrt

class CrossValidationPlotter:
    directory_path: str
    def __init__(self, directory_path: str | None = ...) -> None: ...
    def plot_cross_validation(self, cross_validation: CrossValidation, iteration_number: int|None = ...) -> None: ...
