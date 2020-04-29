from unittest import TestCase, main
import mock

from file_reader import FileReader


class TestFileReader(TestCase):

    def test_file_reader_has_zero_lines_by_default(self):
        """Check that the FileReader has no data in the list_lines attribute"""
        test_object = FileReader()
        self.assertFalse(test_object.list_lines,
                         "list_lines should be empty by default")

    @mock.patch('file_reader.io.open', create=True)
    def test_file_is_open_and_read(self, mocked_open):
        """
        Check that a file is read and the data added to the list_lines
        attribute
        """
        mocked_open.side_effect = [
            mock.mock_open(read_data="Category\tName\tRANKED\tG1\tG2\r"
                                     "CRLF\r\n"
                                     "LF\n"
                                     "No end of file")
                .return_value
        ]
        __file_path = "Path to File"
        test_object = FileReader()
        test_object.read_file(__file_path)
        mocked_open.assert_called_with(__file_path, "r")
        self.assertEqual(4, len(test_object.list_lines),
                         "Should be 4 items in the list")

    @mock.patch('file_reader.io.open', create=True)
    def test_five_hyphens_at_start_ends_read(self, mocked_open):
        """
        Check that a file is read and the data added to the list_lines
        attribute, stopping reading when we see a line that starts with '-----'
        """
        mocked_open.side_effect = [
            mock.mock_open(
                read_data="CR\rCRLF\r\n-----LF\nNo end of file"
            ).return_value
        ]
        __file_path = "Path to File"
        test_object = FileReader()
        test_object.read_file(__file_path)
        mocked_open.assert_called_with(__file_path, "r")
        self.assertEqual(2, len(test_object.list_lines),
                         "Should be 2 items in the list")

    @mock.patch('file_reader.io.open', create=True)
    def test_hash_at_start_skips_line(self, mocked_open):
        """
        Check that a file is read and the data added to the list_lines
        attribute, ignoring lines that start with '#'
        """
        mocked_open.side_effect = [
            mock.mock_open(
                read_data="#CR\rCRLF\r\n# LF\nNo end of file"
            ).return_value
        ]
        __file_path = "Path to File"
        test_object = FileReader()
        test_object.read_file(__file_path)
        mocked_open.assert_called_with(__file_path, "r")
        self.assertEqual(2, len(test_object.list_lines),
                         "Should be 2 items in the list")

    @mock.patch('file_reader.io.open', create=True)
    def test_blank_lines_are_safely_ignored(self, mocked_open):
        """
        Check that a file is read and the data added to the list_lines
        attribute, ignoring any blank lines
        """
        mocked_open.side_effect = [
            mock.mock_open(read_data="Category\tName\tRANKED\tG1\tG2\r"
                                     "CRLF\r\n"
                                     "\n"
                                     "LF\n"
                                     "\n"
                                     "No end of file")
                .return_value
        ]
        __file_path = "Path to File"
        test_object = FileReader()
        test_object.read_file(__file_path)
        mocked_open.assert_called_with(__file_path, "r")
        self.assertEqual(4, len(test_object.list_lines),
                         "Should be 4 items in the list")

    @mock.patch('file_reader.io.open', create=True)
    def test_whitespace_lines_are_safely_ignored(self, mocked_open):
        """
        Check that a file is read and the data added to the list_lines
        attribute, ignoring any lines that are solely whitespace
        """
        mocked_open.side_effect = [
            mock.mock_open(read_data="Category\tName\tRANKED\tG1\tG2\r"
                                     "CRLF\r\n"
                                     "\t\t\n"
                                     "  \n"
                                     "LF\n"
                                     "\n"
                                     "No end of file")
                .return_value
        ]
        __file_path = "Path to File"
        test_object = FileReader()
        test_object.read_file(__file_path)
        mocked_open.assert_called_with(__file_path, "r")
        self.assertEqual(4, len(test_object.list_lines),
                         "Should be 4 items in the list")


if __name__ == '__main__':
    main()
