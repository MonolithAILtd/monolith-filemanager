from unittest import TestCase, main
from unittest.mock import patch, MagicMock

from monolith_filemanager.file.standard_pickle_file import StandardPickleFile


class TestStandardPickleFile(TestCase):

    @patch("monolith_filemanager.file.standard_pickle_file.File.__init__")
    def test___init__(self, mock_file):
        StandardPickleFile(path="test")
        mock_file.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.standard_pickle_file.pickle")
    @patch("monolith_filemanager.file.standard_pickle_file.open")
    @patch("monolith_filemanager.file.standard_pickle_file.StandardPickleFile.__init__")
    def test_read(self, mock_init, mock_open, mock_pickle):
        mock_init.return_value = None
        test = StandardPickleFile(path="test")
        test.path = "test"
        out_come = test.read()

        mock_open.return_value.__enter__.assert_called_once_with()
        self.assertEqual(mock_pickle.load.return_value, out_come)
        mock_open.assert_called_once_with("test", "rb")
        mock_pickle.load.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    @patch("monolith_filemanager.file.standard_pickle_file.pickle")
    @patch("monolith_filemanager.file.standard_pickle_file.open")
    @patch("monolith_filemanager.file.standard_pickle_file.StandardPickleFile.__init__")
    def test_write(self, mock_init, mock_open, mock_pickle):
        mock_init.return_value = None
        test = StandardPickleFile(path="test")
        test.path = "test"
        mock_data = MagicMock()
        test.write(data=mock_data)

        mock_open.assert_called_once_with("test", "wb")
        mock_pickle.dump.assert_called_once_with(mock_data, mock_open.return_value.__enter__.return_value)


if __name__ == "__main__":
    main()
