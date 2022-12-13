from .options import get_parsed_options
from sys import argv
from .. import Maic

def run():
    options = get_parsed_options(argv[1:])

    app = Maic.fromCLI(options)
    # by default running the MAIC app will dump the results (and methodology feature check) in the same format as the input.
    app.run()
