import os
import re
from unittest import TestCase

import mock

from maic import Maic


class TestMaic(TestCase):

    def test_make_output_folder_undefined_path(self):
        """Given an undefined output folder path, we return the blank string"""
        test_object = Maic()
        expected_result = ""
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder=None),
                         "Should get back an empty string for an undefined "
                         "output folder")

    def test_make_output_folder_blank_path(self):
        """Given an empty output folder path, we return the blank string"""
        test_object = Maic()
        expected_result = ""
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder=""),
                         "Should get back an empty string for an output "
                         "folder specified as ''")

    def test_make_output_folder_dot_path(self):
        """Given an output folder path of '.', we return the string './'"""
        test_object = Maic()
        expected_result = ".{}".format(os.sep)
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder='.'),
                         "Should get back '{}' for an output folder "
                         "specified as '.'".format(expected_result))

    @mock.patch('os.makedirs')
    def test_make_output_folder_simple_path(self, mock_makedirs):
        """Given a simple folder path, check that the code tries to make the
        folder and returns the path with a single trailing '/' appended only
        if required"""
        mock_makedirs.return_value = True
        test_object = Maic()
        path = 'simple_path'
        expected_result = '{path}{sep}'.format(path=path, sep=os.sep)
        self.assertTrue(mock_makedirs.called_once_with(path))
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder=path),
                         "Should get back '{expected}' for an output folder"
                         " specified as '{path}'".format(
                             expected=expected_result, path=path)
                         )

    @mock.patch('os.makedirs')
    def test_make_output_folder_simple_path_with_slash(self, mock_makedirs):
        """Given a simple folder path, check that the code tries to make the
        folder and returns the path with a single trailing '/' appended only
        if required"""
        mock_makedirs.return_value = True
        test_object = Maic()
        path = 'simple_path/'
        expected_result = path
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder=path),
                         "Should get back '"
                         + expected_result
                         + "' for an output folder specified as '"
                         + path
                         + "'")
        self.assertTrue(mock_makedirs.called_once_with(path))

    @mock.patch('os.makedirs')
    def test_make_output_folder_path_with_multi_slashes(self, mock_makedirs):
        """Given a complex folder path with multiple embedded slashes,
        check that the code tries to make the folder and returns the path
        with a single trailing '/' appended only if required"""
        mock_makedirs.return_value = True
        test_object = Maic()
        path = '/c/o/m/p/l/e/x_p/a/t/h/'
        expected_result = path
        self.assertEqual(expected_result,
                         test_object.make_output_folder(output_folder=path),
                         "Should get back '"
                         + expected_result
                         + "' for an output folder specified as '"
                         + path
                         + "'")
        self.assertTrue(mock_makedirs.called_once_with(path))

    @mock.patch('logging.Logger.warning')
    @mock.patch('os.makedirs')
    def test_make_output_folder_exists_no_timestamp(self, mock_makedirs,
                                                    mock_logger):
        """Check that an output folder path that exists but does not end
        with something that looks like a timestamp gets a timestamp added"""
        mock_makedirs.side_effect = [OSError, True]
        test_object = Maic()
        path = "my_path"
        sep = os.sep
        if os.sep == '\\':
            # we've got a backslash which causes havoc in a regex so we need
            # to escape the backslash twice
            sep = '\\\\'
        result = test_object.make_output_folder(output_folder=path)
        match_string = r'^my_path-\d{4}(-\d{2}){2}-(-\d{2}){2}' + sep + '$'
        self.assertTrue(
            re.search(match_string, result,
                      re.S),
            "Should have got a path with a Timestamp attached")
        mock_logger.assert_called_with(
            "Specified folder (my_path) already exists - trying to create "
            "one with a timestamp")

    @mock.patch('os.makedirs')
    def test_make_output_folder_exists_with_timestamp_fails(self,
                                                            mock_makedirs):
        """Check that an output folder path that exists and does end with
        something that looks like a timestamp raises an exception"""
        mock_makedirs.side_effect = [OSError]
        test_object = Maic()
        path = "my_path-1960-04-04--15-00"
        try:
            test_object.make_output_folder(output_folder=path)
        except OSError:
            pass
        except BaseException:
            self.fail("Should get an OSError")
