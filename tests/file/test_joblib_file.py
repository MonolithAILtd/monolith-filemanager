
import unittest
from unittest.mock import patch

from monolith_filemanager.file.joblib_file import JoblibFile


class TestJoblibFile(unittest.TestCase):

    @patch("monolith_filemanager.file.joblib_file.File.__init__")
    def test__init_(self, mock_file_init):
        mock_file_init.return_value = None
        JoblibFile(path='test')
        mock_file_init.assert_called_once_with(path='test')

    @patch("monolith_filemanager.file.joblib_file.joblib.load")
    @patch("monolith_filemanager.file.joblib_file.JoblibFile.__init__")
    def test_read(self, mock_init, mock_joblib_load):
        mock_init.return_value = None
        test = JoblibFile(path="test")
        test.path = "/some/path.joblib"
        test.read()

        mock_init.assert_called_once_with(path="test")
        mock_joblib_load.assert_called_once_with("/some/path.joblib")

    @patch("monolith_filemanager.file.joblib_file.joblib.dump")
    @patch("monolith_filemanager.file.joblib_file.JoblibFile.__init__")
    def test_write(self, mock_init, mock_joblib_dump):
        mock_init.return_value = None
        test = JoblibFile(path="test")
        test.path = "/some/path.joblib"
        test.write(data="string object")

        mock_init.assert_called_once_with(path="test")
        mock_joblib_dump.asssert_called_once_with(
            "string object", "/some/path.joblib"
        )


if __name__ == '__main__':
    unittest.main()
