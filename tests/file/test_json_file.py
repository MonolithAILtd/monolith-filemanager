import unittest
from unittest.mock import patch

from monolith_filemanager.file.json_file import JSONFile


class TestJSONFile(unittest.TestCase):

    @patch("monolith_filemanager.file.json_file.File.__init__")
    def test__init_(self, mock_file_init):
        mock_file_init.return_value = None
        JSONFile(path='test')
        mock_file_init.assert_called_once_with(path='test')

    @patch("monolith_filemanager.file.json_file.json.load")
    @patch("monolith_filemanager.file.json_file.JSONFile.__init__")
    @patch("monolith_filemanager.file.json_file.open")
    def test_read(self, mock_open, mock_init, mock_json_load):
        mock_init.return_value = None
        test = JSONFile(path="test")
        test.path = "/some/path.json"
        test.read()

        mock_init.assert_called_once_with(path="test")
        mock_json_load.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    @patch("monolith_filemanager.file.json_file.json.dump")
    @patch("monolith_filemanager.file.json_file.JSONFile.__init__")
    @patch("monolith_filemanager.file.json_file.open")
    def test_write(self, mock_open, mock_init, mock_json_dump):
        mock_init.return_value = None
        test = JSONFile(path="test")
        test.path = "/some/path.json"
        test.write(data="string object")

        mock_init.assert_called_once_with(path="test")
        mock_json_dump.asssert_called_once_with(
            mock_open.return_value.__enter__.return_value, "string object"
        )


if __name__ == '__main__':
    unittest.main()
