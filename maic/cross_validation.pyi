from .entity import Entity as Entity
from .entitylist import EntityList
from maic.io.cv_dumper import CrossValidationDumper as CrossValidationDumper
from maic.io.cv_plotter import CrossValidationPlotter as CrossValidationPlotter
from typing import MutableSequence, Sequence, tuple
from numpy import floating

POST_ITERATION_CALLBACK: str

class CrossValidation:
    entities: MutableSequence[Entity]
    entity_lists: MutableSequence[EntityList]
    threshold: float
    max_iterations: int
    transform_methods: str|list[str]
    plotter: CrossValidationPlotter
    callbacks:dict[str, Sequence[CrossValidationDumper]]
    def __init__(self, entities: MutableSequence[Entity], entity_lists: MutableSequence[EntityList], threshold: float, max_iterations: int, transform_methods: str|list[str] = ...) -> None: ...
    def run_analysis(self) -> None: ...
    def register_callback(self, callback_type: str, callback_object: CrossValidationDumper): ...
    def code_string(self) -> str: ...
    def summary_data(self) -> tuple[floating, floating]: ...
