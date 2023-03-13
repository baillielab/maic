from maic.cross_validation import CrossValidation
from maic.entity import Entity
from maic.entitylist import EntityList
from typing import Sequence

class GeneScoresDumper:
    cross_validation: CrossValidation
    output_folder: str
    def __init__(self, cross_validation: CrossValidation, output_folder: str | None = ...) -> None: ...
    def lists_in_category_order(self) -> Sequence[EntityList]: ...
    def build_file_and_method_name(self, method: str=..., baseline: str | None = ...) -> FileAndMethodName: ...
    def dump(self, method: str=..., baseline: str | None = ...) -> None: ...
    def entities_in_descending_score_order(self, method:str=...) -> Sequence[Entity]: ...
    def extra_headers(self) -> Sequence[str]: ...
    def score_for_entity_from_list(self, entity: Entity, lst: EntityList) -> int|float: ...
    def additional_column_data(self, entity: Entity) -> Sequence[str]: ...
    def dataset_feature_check_to_choice_methods(self) -> None: ...

class AllScoresGeneScoresDumper(GeneScoresDumper):
    def extra_headers(self) -> Sequence[str]: ...
    def score_for_entity_from_list(self, entity: Entity, lst: EntityList) -> int|float: ...
    def additional_column_data(self, entity: Entity) -> Sequence[str]: ...

class IterationAwareGeneScoresDumper(AllScoresGeneScoresDumper):
    iteration: int
    def __init__(self, cross_validation: CrossValidation, output_folder: str | None = ...) -> None: ...
    def build_file_and_method_name(self, method=..., baseline: str | None = ...) -> FileAndMethodName: ...

class FileAndMethodName:
    filename: str
    methodname: str
    def __init__(self) -> None: ...