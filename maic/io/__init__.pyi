from ..models import EntityListModel
from enum import Enum
from typing import Sequence, Literal

class Format(Enum):
    MAIC: Literal["MAIC"]
    JSON: Literal["JSON"]
    YAML: Literal["YAML"]

def read_file(filepath: str, *args, format: Format = ...) -> Sequence[EntityListModel]: ...
