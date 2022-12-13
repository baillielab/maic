from typing import Sequence
from ..models import EntityListModel
from ..errors import WarnValueError
from enum import Enum

import logging
logger = logging.getLogger(__name__)

FORMAT = Enum("Format", "MAIC JSON YAML")

def read_file(filepath: str, *args, format: FORMAT = FORMAT.MAIC) -> Sequence[EntityListModel]:
    
    def parse_json(file):
        from json import load
        data = load(file)

        return [EntityListModel(name=i['name'], category=i['category'], ranked=i['ranked'], entities=i['entities']) for i in data]

    def parse_yaml(file):
        from oyaml import load, Loader
        data = load(file, Loader)

        return [EntityListModel(name=i['name'], category=i['category'], ranked=i['ranked'], entities=i['entities']) for i in data]

    def parse_maic(file):
        from re import match
        data = []
        for line in file:
            if line.startswith("-----"):
                # stop processing the file at this point
                return data
            if line.startswith("#") or match(r"^\s*$", line):
                # empty or commented line: ignore
                continue

            # process the line of data:
            columns = line.strip().split("\t")
            if len(columns) < 4:
                # per docstring this isn't meant to break processing, but 'raise'ing will.
                # need to revisit this logic.
                raise WarnValueError('Insufficient columns to create an EntityList')

            elm = EntityListModel(name=columns[1], category=columns[0], ranked=(columns[2].strip().upper() == "RANKED"), entities=[])
            for i, word in enumerate(columns[4:], 4):
                if match(r"^\s*$", word):
                    # blank column, need to log the error:
                    logger.info(f"Blank Column: list {elm.name}, column {i}")
                else:
                    elm.entities.append(word)
            
            data.append(elm)

        return data

    parsers = {
        FORMAT.MAIC: parse_maic,
        FORMAT.YAML: parse_yaml,
        FORMAT.JSON: parse_json
    }

    if format not in parsers:
        raise ValueError(f"Unknown file format: {format}")

    with open(filepath, "r") as file:
        return parsers[format](file)