import logging
from os.path import expanduser, exists


logging.basicConfig()
logger = logging.getLogger(__name__)


class Baseline(object):
    """Object to represent a Baseline measuement from a random simulated data
    set"""

    def __init__(self, code_string, base_score, base_stdev, num_perms, model):
        """Initialise a Baseline object using the required parameters"""
        self.code_string = code_string
        self.base_score = base_score
        self.base_stdev = base_stdev
        self.num_perms = num_perms
        self.model = model

    def __str__(self):
        """Convert the object to a string for display"""
        # @formatter:off
        return "code string: %s\n" \
               "model: %s\n" \
               "permutations: %s\n" \
               "baseline: %f\n" \
               "stdev: %f\n" \
               % \
               (self.code_string,
                self.model,
                self.num_perms,
                self.base_score,
                self.base_stdev)
        # @formatter:on


def get_baseline_from_store(file_path, version, code_string, model,
                            permutations):
    """Look for a baseline that matches the specified conditions. Return
    None if nothing matches.
    :param file_path: path to the file to query
    :param version: version of the code that we want to match
    :param code_string: the pattern of the data specified as a code string
    :param model: the model used to map the weights
    :param permutations: the minimum number of permutations used to generate
    the baseline"""
    return_value = None
    matches = []
    highest_permutations = 0
    best_match = -1
    home = expanduser("~")
    file_path= file_path.replace("${HOME}", home)
    if exists(file_path):
        logger.debug("opening the baselines file at %s" % file_path)
        with open(file_path, "r") as baseline_file:
            print("all good")
            for line in baseline_file.read().splitlines():
                logger.debug("Got a line (%s)" % line)
                cols = line.split("\t")
                # not enough columns
                if len(cols) < 5:
                    logger.debug("Bailing - not enough columns")
                    continue
                # wrong code version
                if cols[0] != str(version):
                    logger.debug("Bailing - wrong version")
                    continue
                # wrong model
                if cols[1] != model:
                    logger.debug("Bailing - wrong model")
                    continue
                # not enough permutations
                if int(cols[2]) < permutations:
                    logger.debug("Bailing - not enough permutations")
                    continue
                # wrong data pattern
                if cols[3] != code_string:
                    logger.debug("Bailing - wrong code string")
                    continue
                # Build a Baseline object and put it in a list (there may be
                # multiple matches
                matches.append(
                    Baseline(code_string=code_string, base_score=cols[4],
                             base_stdev=cols[5], num_perms=int(cols[2]),
                             model=model))
                # If this has more permutations than any previous match then
                # note its index. If it matches a previous one, use this one
                # because it will be a later calculation
                if int(cols[2]) >= highest_permutations:
                    logger.debug("Got a match - better than anything we've seen "
                                 "so far")
                    best_match = len(matches) - 1
                else:
                    logger.debug("Got a match - previous one was better")

        # If we got matches, use the one that was the best match
        if len(matches) > 0:
            return_value = matches[best_match]
    else:
        logger.info("No baselines file at %s" % file_path)

    return return_value


def put_baseline_to_store(file_path, version, baseline):
    """Look for a baseline that matches the specified conditions. Return
    None if nothing matches.
    :param file_path: path to the file to store into
    :param version: version of the code that we have used
    :param baseline: the baseline object to store"""
    home = expanduser("~")
    file_path= file_path.replace("${HOME}", home)
    with open(file_path, "a") as baseline_file:
        baseline_file.write('\t'.join(
            [str(version), baseline.model, str(baseline.num_perms),
             baseline.code_string, str(baseline.base_score),
             str(baseline.base_stdev)]) + "\n")
