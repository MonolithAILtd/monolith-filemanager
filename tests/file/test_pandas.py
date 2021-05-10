from unittest import TestCase, main
from unittest.mock import patch, MagicMock
from monolith_filemanager.file.pandas_file import PandasFile
import pandas as pd

LOADING_METHODS = {
    "h5": pd.read_hdf,
    "parquet": pd.read_parquet,
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "dat": pd.read_table,
    "data": pd.read_table
}


class TestPandasFile(TestCase):

    @patch("monolith_filemanager.file.pandas_file.File.__init__")
    def test___init__(self, mock_file_init):
        PandasFile(path="test")
        mock_file_init.return_value = None
        mock_file_init.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__")
    def test__map_write_functions(self, mock_init):
        mock_init.return_value = None
        test = PandasFile(path="test")
        test.path = MagicMock()
        test.path.file_type = "csv"
        test_input = MagicMock()
        out_come = test._map_write_functions(data=test_input)

        self.assertEqual(test_input.to_csv, out_come)
        self.assertEqual(test_input.to_csv("test path"), out_come("test path"))

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__")
    def test_read(self, mock_init):
        mock_init.return_value = None
        test = PandasFile(path="test")
        test.path = MagicMock()
        test.path.file_type = "csv"
        test.LOADING_METHODS["csv"] = MagicMock()
        out_come = test.read()

        self.assertEqual(test.LOADING_METHODS["csv"].return_value, out_come)
        test.LOADING_METHODS["csv"].assert_called_once_with(test.path)

    @patch("monolith_filemanager.file.pandas_file.PandasFile._map_write_functions")
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__")
    def test_write(self, mock_init, mock_map):
        mock_init.return_value = None
        test = PandasFile(path="test")

        test.path = MagicMock()
        test_data = pd.DataFrame([{"one": 1, "two": 2}, {"one": 1, "two": 2}])

        test.write(data=test_data)

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

        mock_map.assert_called_once_with(data=test_data)
        mock_map.return_value.assert_called_once_with(test.path, header=True, index=False)


if __name__ == "__main__":
    main()
