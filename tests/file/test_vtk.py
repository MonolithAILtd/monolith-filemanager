from unittest import TestCase, main
from unittest.mock import patch, MagicMock

from monolith_filemanager.file.vtk_file import VtkFile


class TestStlFile(TestCase):

    @patch("monolith_filemanager.file.vtk_file.File.__init__")
    def test___init__(self, mock_file):
        VtkFile(path="test")
        mock_file.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.vtk_file.expand_3d_point_arrays")
    @patch("monolith_filemanager.file.vtk_file.File.__init__")
    @patch("pyvista.read")
    def test_read(self, mock_pv_read, mock_file, mock_expand_3d_point_arrays):
        mock_file.return_value = None
        test = VtkFile(path="test")
        test.path = "test"
        res = test.read()
        mock_expand_3d_point_arrays.assert_called_once_with(mock_pv_read.return_value)
        self.assertEqual(res, mock_expand_3d_point_arrays.return_value)

    @patch("monolith_filemanager.file.vtk_file.File.__init__")
    def test_write(self, mock_file):
        mock_file.return_value = None
        test = VtkFile(path="test")
        test.path = "test"
        mock_data = MagicMock()
        test.write(data=mock_data)
        mock_data.save.assert_called_once_with("test")


if __name__ == "__main__":
    main()
