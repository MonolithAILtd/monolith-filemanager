from unittest import TestCase, main
from unittest.mock import patch, MagicMock

from general_filemanager.file.pickle_file import PickleFile, PickleFileError


class TestPickleFile(TestCase):

    @patch("general_filemanager.file.pickle_file.File.__init__")
    def test___init__(self, mock_file):
        PickleFile(path="test")
        mock_file.assert_called_once_with(path="test")

    @patch("general_filemanager.file.pickle_file.File.__init__")
    @patch("general_filemanager.file.pickle_file.open")
    def test_read(self, mock_open, mock_file):
        mock_file.return_value = None
        test = PickleFile(path="test")
        test.path = "test"
        with self.assertRaises(PickleFileError):
            test.read()

    @patch("general_filemanager.file.pickle_file.File.__init__")
    @patch("general_filemanager.file.pickle_file.open")
    def test_write(self, mock_open, mock_file):
        mock_file.return_value = None
        test = PickleFile(path="test")
        test.path = "test"
        mock_data = MagicMock()
        with self.assertRaises(PickleFileError):
            test.write(data=mock_data)


if __name__ == "__main__":
    main()
