import logging
from datetime import datetime
from time import sleep, strftime
from unittest import TestCase

import options
from maic.constants import T_METHOD_NONE, T_METHOD_MEAN, T_METHOD_STEM_SCALE, \
    T_METHOD_STEM_ADJUST, S_METHOD_NONE, S_METHOD_Z_TRANSFORM, \
    S_METHOD_STEM_POW

EXPECTED_OPTION_ATTRIBUTE_KEYS = [
    'dump',
    'filename',
    'logging_level',
    'max_input_len',
    'max_iterations',
    'output_folder',
    'plot',
    'random_source_len',
    'stability',
    'weight_function'
]
EXPECTED_OPTION_ATTRIBUTE_COUNT = len(EXPECTED_OPTION_ATTRIBUTE_KEYS)

# Keep these in sync with those defined in the options.py file. These are
# here because we rely on the string values within code and changing them in
# the options.py file without the check might lead to unintended changes in
# behaviour if the code that uses the option values was not kept up to date
EXPECTED_TRANSFORM_STANDARD_OPTIONS = [T_METHOD_NONE, T_METHOD_MEAN]
EXPECTED_TRANSFORM_EXTENDED_OPTIONS = [T_METHOD_STEM_SCALE,
                                       T_METHOD_STEM_ADJUST]

EXPECTED_SCALE_STANDARD_OPTIONS = [S_METHOD_NONE, S_METHOD_Z_TRANSFORM]
EXPECTED_SCALE_EXTENDED_OPTIONS = [S_METHOD_STEM_POW]


class TestOptions(TestCase):

    def test_attribute_list_matches_expected(self):
        """Check that the attribute list of the returned Namespace object
        only contains the attributes that we expect (and contains all of
        them.
        """
        test_object = options.get_parsed_options()
        key_list = vars(test_object).keys()
        self.assertEqual(EXPECTED_OPTION_ATTRIBUTE_COUNT, len(key_list))
        for key in EXPECTED_OPTION_ATTRIBUTE_KEYS:
            self.assertTrue(key in key_list,
                            "Didn't find '%s' in the list" % key)

    def test_default_filename(self):
        """Check the default filename value matches the expected value
        (None)."""
        test_object = options.get_parsed_options()
        self.assertIsNone(test_object.filename,
                          'Unexpected value for filename')

    def test_filename_is_settable(self):
        """Check that we can set a value for filename by passing in a
        suitable set of parameters on the 'command line'.
        """
        set_filename = "My new Filename"
        test_object = options.get_parsed_options(['--filename', set_filename])
        self.assertEqual(set_filename, test_object.filename,
                         'Unexpected value for filename')

    def test_default_max_input_len(self):
        """Check the default max_input_len value matches the expected value."""
        test_object = options.get_parsed_options()
        self.assertEqual(2000, test_object.max_input_len,
                         'Unexpected value for max_input_len')

    def test_default_random_source_len(self):
        """Check the default random_source_len value matches the expected
        value.
        """
        test_object = options.get_parsed_options()
        self.assertEqual(20000, test_object.random_source_len,
                         'Unexpected value for random_source_len')

    def test_default_stability(self):
        """Check the default stability value matches the expected
        value.
        """
        test_object = options.get_parsed_options()
        self.assertEqual(0.01, test_object.stability,
                         'Unexpected value for stability')

    def test_default_max_iterations(self):
        """Check the default max_iterations value matches the expected
        value.
        """
        test_object = options.get_parsed_options()
        self.assertEqual(100, test_object.max_iterations,
                         'Unexpected value for max_iterations')

    def test_default_logging_level_is_warn(self):
        """Check that the default logging level is reported as warn"""
        test_object = options.get_parsed_options()
        self.assertEqual(logging.WARN, test_object.logging_level,
                         'Default logging level should be "warn"')

    def test_single_v_equals_log_level_warn(self):
        """Check that a single verbose flag leaves logging level
        at warn"""
        test_object = options.get_parsed_options(["-v"])
        self.assertEqual(logging.WARN, test_object.logging_level,
                         'Logging level should be "warn" with 1 "v" arg')

    def test_can_set_info_log_level(self):
        """Check that we can set the logging level to info by specifying
        -vv"""
        test_object = options.get_parsed_options(["-vv"])
        self.assertEqual(logging.INFO, test_object.logging_level,
                         'Logging level should be "info" with 2 "v" args')

    def test_can_set_debug_log_level(self):
        """Check that we can set the logging level to debug by specifying
        -vvv"""
        test_object = options.get_parsed_options(["-vvv"])
        self.assertEqual(logging.DEBUG, test_object.logging_level,
                         'Logging level should be "debug" with 3 "v" args')

    def test_single_v_equals_log_level_warn_long(self):
        """Check that a single --verbose flag leaves logging level
        at warn"""
        test_object = options.get_parsed_options(["--verbose"])
        self.assertEqual(logging.WARN, test_object.logging_level,
                         'Logging level should be "warn" with 1 "verbose" arg')

    def test_can_set_info_log_level_long(self):
        """Check that we can set the logging level to info by specifying
        --verbose --verbose"""
        test_object = options.get_parsed_options(["--verbose", "--verbose"])
        self.assertEqual(logging.INFO, test_object.logging_level,
                         'Logging level should be "info" with 2 "verbose" '
                         'args')

    def test_can_set_debug_log_level_long(self):
        """Check that we can set the logging level to debug by specifying
        --verbose --verbose --verbose"""
        test_object = options.get_parsed_options(
            ["--verbose", "--verbose", "--verbose"])
        self.assertEqual(logging.DEBUG, test_object.logging_level,
                         'Logging level should be "debug" with 3 "verbose" '
                         'args')

    def test_can_set_error_log_level(self):
        """Check that a single quiet flag pushes logging level
        to error"""
        test_object = options.get_parsed_options(["-q"])
        self.assertEqual(logging.ERROR, test_object.logging_level,
                         'Logging level should be "error" with 1 "q" arg')

    def test_can_set_critical_log_level(self):
        """Check that we can set the logging level to critical by specifying
        -qq"""
        test_object = options.get_parsed_options(["-qq"])
        self.assertEqual(logging.CRITICAL, test_object.logging_level,
                         'Logging level should be "critical" with 2 "q" args')

    def test_can_set_error_log_level_long(self):
        """Check that a single quiet flag pushes logging level
        to error"""
        test_object = options.get_parsed_options(["--quiet"])
        self.assertEqual(logging.ERROR, test_object.logging_level,
                         'Logging level should be "error" with 1 "quiet" arg')

    def test_can_set_critical_log_level_long(self):
        """Check that we can set the logging level to critical by specifying
        -qq"""
        test_object = options.get_parsed_options(["-qq"])
        self.assertEqual(logging.CRITICAL, test_object.logging_level,
                         'Logging level should be "critical" with 2 "quiet" '
                         'args')

    def test_quiet_overrules_verbose(self):
        """Check that quiet flags override the verbose flags"""
        test_object = options.get_parsed_options(["-vvvv", "-q"])
        self.assertEqual(logging.ERROR, test_object.logging_level,
                         'Logging level should be "error" with 1 "quiet" '
                         'arg regardless of how many "verbose" flags are set')

    def test_output_folder_is_none_by_default(self):
        """Check that output folder is None in a 'naked' options parsing"""
        test_object = options.get_parsed_options()
        self.assertIsNone(test_object.output_folder,
                          "output folder should be None by default")

    def test_output_folder_uses_filename_plus_timestamp_by_default(self):
        """If we have a filename but no output folder then we expect a
        default output folder to be constructed from the basename of the
        input file plus a date/timestamp"""
        filename_base = "input-file-23.a.b.c"
        filename = filename_base + ".txt"

        # Wait so we don't get failures due to the minute ticking over
        while datetime.now().second > 57:
            sleep(1)
        timestamp = strftime("%Y-%m-%d--%H-%M")
        expected_name = filename_base + "-" + timestamp
        test_object = options.get_parsed_options(['--filename', filename])
        self.assertEqual(expected_name, test_object.output_folder,
                         "Expected output folder to be filename base plus "
                         "timestamp")

    def test_output_folder_is_settable(self):
        """Check that output folder can be set"""
        output_folder_name = "output-folder-that-we-set"
        test_object = options.get_parsed_options(
            ['--output-folder', output_folder_name])
        self.assertEqual(output_folder_name, test_object.output_folder,
                         "output folder should be what we just set")

    def test_default_plot_is_false(self):
        """Check that the default value for the plot attribute is False"""
        test_object = options.get_parsed_options()
        self.assertFalse(test_object.plot,
                         "'plot' attribute should be False by default")

    def test_plot_is_settable(self):
        """Check that we can set the plot attribute"""
        test_object = options.get_parsed_options(['--plot'])
        self.assertTrue(test_object.plot,
                        "'plot' attribute should be True when set")
