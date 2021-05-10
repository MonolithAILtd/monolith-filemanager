from unittest import TestCase, main
from unittest.mock import patch

from general_filemanager.path import FilePath


class TestFilePath(TestCase):

    @patch("general_filemanager.path.FilePath.check_if_s3")
    @patch("general_filemanager.path.FilePath.get_file_type")
    def test___init__(self, mock_get_file_type, mock_check_if_s3):
        test = FilePath("this/is/a/path.txt")

        self.assertEqual("path.txt", test.file)
        self.assertEqual("this/is/a/", test.root)
        self.assertEqual(mock_get_file_type.return_value, test.file_type)
        self.assertEqual(mock_check_if_s3.return_value, test.s3)
        mock_get_file_type.assert_called_once_with(file_string="path.txt")

    def test_check_if_s3(self):
        self.assertEqual(True, FilePath.check_if_s3(path_string="s3://test"))
        self.assertEqual(False, FilePath.check_if_s3(path_string="test"))

    def test_get_file_type(self):
        self.assertEqual("txt", FilePath.get_file_type(file_string="test.txt"))
        self.assertIsNone(FilePath.get_file_type(file_string="testtxt"))

    @patch("general_filemanager.path.os")
    @patch("general_filemanager.path.FilePath.__init__")
    def test_root_exists(self, mock_init, mock_os):
        mock_init.return_value = None
        test = FilePath("test")
        test.root = "test"
        out_come = test.root_exists

        self.assertEqual(mock_os.path.isdir.return_value, out_come)
        mock_os.path.isdir.assert_called_once_with(test.root)

    @patch("general_filemanager.path.os")
    @patch("general_filemanager.path.FilePath.__init__")
    def test_file_exists(self, mock_init, mock_os):
        mock_init.return_value = None
        test = FilePath("this/is/a/path.txt")

        out_come = test.file_exists

        self.assertEqual(mock_os.path.exists.return_value, out_come)
        mock_os.path.exists.assert_called_once_with(test)


if __name__ == "__main__":
    main()
