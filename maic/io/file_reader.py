import io
import re


class FileReader(object):

    def __init__(self):
        """Initialise a FileReader object"""
        self.list_lines = []

    def read_file(self, file_path):
        """
        Read the supplied file into memory
        Skips lines that begin with a hash character and stops reading the
        file when it encounters a line that begins with 5 or more hyphens
        """
        with io.open(file_path, "r") as input_file:
            for line in input_file.read().splitlines():
                if line.startswith("-----"):
                    break
                elif re.match("^\\s*$", line):
                    pass
                elif not line.startswith("#"):
                    self.list_lines.append(line)
