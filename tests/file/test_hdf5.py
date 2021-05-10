from unittest import TestCase, main
from unittest.mock import patch, MagicMock
from monolith_filemanager.file.hdf5_file import Hdf5File


class TestHdf5File(TestCase):

    @patch("monolith_filemanager.file.hdf5_file.File.__init__")
    def test___init__(self, mock_file):
        Hdf5File(path="test")
        mock_file.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.hdf5_file.h5py")
    @patch("monolith_filemanager.file.hdf5_file.File.__init__")
    def test_read(self, mock_file, mock_h5py):
        mock_file.return_value = None
        test = Hdf5File(path="test")
        test.path = "test"
        out_come = test.read()
        mock_h5py.File.assert_called_once_with("test", mode='r')
        self.assertEqual(mock_h5py.File.return_value, out_come)

    @patch("monolith_filemanager.file.pickle_file.File.__init__")
    def _test_write(self, mock_file):
        mock_file.return_value = None
        # No write method to test at the moment


if __name__ == "__main__":
    main()
