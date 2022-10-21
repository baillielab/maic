from ..models import EntityListModel

def read_file(filepath, *args, format="maic"):
    
    def parse_json(file):
        pass

    def parse_yaml(file):
        pass

    def parse_maic(file):
        pass

    parsers = {
        "maic": parse_maic,
        "yaml": parse_yaml,
        "json": parse_json
    }

    if format not in parsers:
        raise ValueError(f"Uknown file format: {format}")

    with open(filepath, "r") as file:
        return parsers[format](file)