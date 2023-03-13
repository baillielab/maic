from typing import Sequence
from .entity import Entity as Entity
from .models import EntityListModel as EntityListModel
from threading import Lock

FAILED_RANKED_LIST_DESCENT_STEP: float

class EntityList:
    @staticmethod
    def frommodel(elm: EntityListModel, *args, entities: dict[str, Entity] = ..., limit: int = ...) -> EntityList: ...
    lock: Lock
    is_ranked: bool
    weight: int
    delta: float
    category_name: str
    name: str
    base_score_mean: float
    base_score_stdev: float
    need_local_baseline_base_score_mean: float
    weights_list: Sequence[int|float]
    def __init__(self, name: str = ..., category: str = ..., is_ranked: bool = ...) -> None: ...
    def reset(self) -> None: ...
    def append(self, entity: Entity) -> None: ...
    def get_truncated_weights_list(self) -> Sequence[float]: ...
    @property
    def category(self) -> str: ...
    def __setattr__(self, key, value) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def calculate_new_weight(self): ...
    def get_weight_for_entity(self, entity) -> int|float: ...
    def code_string(self) -> str: ...

class ExponentialEntityList(EntityList):
    @staticmethod
    def frommodel(elm: EntityListModel, *args, entities: dict[str, Entity] = ..., limit: int = ...) -> ExponentialEntityList: ...
    fit_parameters: Sequence[int|float]
    def __init__(self, name: str = ..., category: str = ..., is_ranked: bool = ...) -> None: ...
    def reset(self) -> None: ...