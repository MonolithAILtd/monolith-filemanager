import tempfile
from unittest import TestCase, main
from unittest.mock import patch, MagicMock

import dask.dataframe as dd
import pandas as pd
from dask.dataframe.utils import assert_eq
from pandas.testing import assert_frame_equal
from parameterized import parameterized

from monolith_filemanager.file.errors import PandasFileError
from monolith_filemanager.file.pandas_file import PandasFile

file_types = PandasFile.SUPPORTED_FORMATS
CHUNK_SIZE = '256MB'
STORAGE_OPTIONS = {'config_kwargs': {'max_pool_connections': 32}}

class TestPandasFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.TemporaryDirectory()
        cls.example_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        cls.example_df.to_parquet(f'{cls.test_dir.name}/data.parquet')
        cls.example_df.to_csv(f'{cls.test_dir.name}/data.csv', index=False)
        cls.example_df.to_excel(f'{cls.test_dir.name}/data.xls', index=False)
        cls.example_df.to_excel(f'{cls.test_dir.name}/data.xlsx', index=False)
        cls.example_df.to_csv(f'{cls.test_dir.name}/data.dat', index=False, sep=',')
        cls.example_df.to_csv(f'{cls.test_dir.name}/data.data', index=False, sep=',')

    @classmethod
    def tearDownClass(cls):
        cls.test_dir.cleanup()

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

        test.write(data=test_data, repartition=False)

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

        mock_map.assert_called_once()
        assert_eq(mock_map.call_args[1]['data'], test_data_dask, check_divisions=False)
        mock_map.return_value.assert_called_once_with(test.path, compute_kwargs={'scheduler': 'threads'})

    @patch("monolith_filemanager.file.pandas_file.PandasFile._map_write_functions")
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_write_with_callback(self, _, mock_map):
        test = PandasFile(path="test")
        cb = MagicMock()

        test.path = MagicMock()
        test_data = pd.DataFrame([{"one": 1, "two": 2}, {"one": 1, "two": 2}])
        test_data_dask = dd.from_pandas(test_data, npartitions=1)

        test.write(data=test_data, cb=cb)

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

        mock_map.assert_called_once()
        assert_eq(mock_map.call_args[1]['data'], test_data_dask, check_divisions=False)
        mock_map.return_value.assert_called_once_with(test.path, compute_kwargs={'scheduler': 'threads'})

        cb.__enter__.assert_called_once()
        cb.__exit__.assert_called_once()

    @patch("monolith_filemanager.file.pandas_file.PandasFile._read_dask", return_value=None)
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_read_lazy(self, _, mock__read_dask):
        PandasFile(path='test').read(lazy=True)
        mock__read_dask.assert_called_once_with(CHUNK_SIZE, storage_options=STORAGE_OPTIONS)

    @patch("monolith_filemanager.file.pandas_file.PandasFile._read_dask", return_value=MagicMock())
    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_read_eager(self, _, mock__read_dask):
        PandasFile(path='test').read(lazy=False)
        mock__read_dask.assert_called_once_with(CHUNK_SIZE, storage_options=STORAGE_OPTIONS)

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test__read_dask_invalid_filetype(self, _):
        test = PandasFile(path='test')
        test.path = MagicMock()
        test.path.file_type = 'INVALID FILETYPE'

        with self.assertRaises(PandasFileError):
            _ = test._read_dask(chunk_size=1)



    @parameterized.expand([(f, lazy) for f in file_types for lazy in (True, False)])
    def test_read_functional(self, file_type, lazy):
        file = PandasFile(path=f'{self.test_dir.name}/data.{file_type}')

        if file_type in ('dat', 'data'):
            df = file.read(lazy=lazy, sep=',')
        else:
            df = file.read(lazy=lazy)

        if lazy:
            self.assertIsInstance(df, dd.DataFrame)
            df = df.compute()

        self.assertIsInstance(df, pd.DataFrame)
        assert_frame_equal(df, self.example_df)


if __name__ == "__main__":
    main()
