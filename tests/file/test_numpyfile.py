from unittest import TestCase, main
from unittest.mock import patch
from monolith_filemanager.file.numpy_file import NumpyFile


class TestNumpyFile(TestCase):

    @patch("monolith_filemanager.file.numpy_file.File.__init__")
    def test___init__(self, mock_file_init):
        NumpyFile(path="test")
        mock_file_init.return_value = None
        mock_file_init.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.numpy_file.np")
    @patch("monolith_filemanager.file.numpy_file.NumpyFile.__init__")
    def test_read_file(self, mock_init, mock_np):
        mock_init.return_value = None
        test = NumpyFile(path="test")
        test.path = "/some/path.npy"
        test.read()

        mock_init.assert_called_once_with(path="test")
        mock_np.load.assert_called_once_with("/some/path.npy")

    @patch("monolith_filemanager.file.numpy_file.np")
    @patch("monolith_filemanager.file.numpy_file.NumpyFile.__init__")
    def test_write_file(self, mock_init, mock_np):
        mock_init.return_value = None
        test = NumpyFile(path="test")
        test.path = "/some/path.npy"
        test.write(data="string object")

        mock_init.assert_called_once_with(path="test")
        mock_np.save.assert_called_once_with("/some/path.npy", "string object", allow_pickle=False)


if __name__ == "__main__":
    main()
