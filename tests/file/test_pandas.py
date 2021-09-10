from unittest import TestCase, main
from unittest.mock import patch, MagicMock

import dask.dataframe as dd
import pandas as pd
from dask.dataframe.utils import assert_eq

from monolith_filemanager.file.errors import PandasFileError
from monolith_filemanager.file.pandas_file import PandasFile

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

    @patch("monolith_filemanager.file.pandas_file.PandasFile._map_write_functions")
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__")
    def test_write(self, mock_init, mock_map):
        mock_init.return_value = None
        test = PandasFile(path="test")

        test.path = MagicMock()
        test_data = pd.DataFrame([{"one": 1, "two": 2}, {"one": 1, "two": 2}])
        test_data_dask = dd.from_pandas(test_data, npartitions=1)

        test.write(data=test_data)

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

        mock_map.assert_called_once()
        assert_eq(mock_map.call_args[1]['data'], test_data_dask)
        mock_map.return_value.assert_called_once_with(test.path, compute_kwargs={'scheduler': 'threads'})

    @patch("monolith_filemanager.file.pandas_file.PandasFile._read_dask", return_value=None)
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_read_lazy(self, _, mock__read_dask):
        PandasFile(path='test').read(lazy=True)
        mock__read_dask.assert_called_once_with('64MB')

    @patch("monolith_filemanager.file.pandas_file.PandasFile._read_pandas", return_value=None)
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_read_eager(self, _, mock__read_pandas):
        PandasFile(path='test').read(lazy=False)
        mock__read_pandas.assert_called_once_with()

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test__read_dask_valid_filetype(self, _):
        test = PandasFile(path='test')
        test.path = MagicMock()
        test.path.file_type = 'csv'
        test.DASK_LOADING_METHODS['csv'] = MagicMock()

        result = test._read_dask(chunk_size=1)

        self.assertEqual(test.DASK_LOADING_METHODS['csv'].return_value, result)
        test.DASK_LOADING_METHODS['csv'].assert_called_once_with(test.path, chunksize=1, block_size=1)

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test__read_dask_invalid_filetype(self, _):
        test = PandasFile(path='test')
        test.path = MagicMock()
        test.path.file_type = 'INVALID FILETYPE'

        with self.assertRaises(PandasFileError):
            _ = test._read_dask(chunk_size=1)

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test__read_pandas_valid_filetype(self, _):
        test = PandasFile(path='test')
        test.path = MagicMock()
        test.path.file_type = 'csv'
        test.PANDAS_LOADING_METHODS['csv'] = MagicMock()

        result = test._read_pandas()

        self.assertEqual(test.PANDAS_LOADING_METHODS['csv'].return_value, result)
        test.PANDAS_LOADING_METHODS['csv'].assert_called_once_with(test.path)

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test__read_pandas_invalid_filetype(self, _):
        test = PandasFile(path='test')
        test.path = MagicMock()
        test.path.file_type = 'INVALID FILETYPE'

        with self.assertRaises(PandasFileError):
            _ = test._read_pandas(chunk_size=1)


if __name__ == "__main__":
    main()
