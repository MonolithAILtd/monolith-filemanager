import tempfile
from unittest import TestCase, main
from unittest.mock import patch, MagicMock

import dask.dataframe as dd
import pandas as pd
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal, assert_index_equal
from parameterized import parameterized

from monolith_filemanager.file.errors import PandasFileError
from monolith_filemanager.file.pandas_file import PandasFile

file_types = PandasFile.SUPPORTED_FORMATS
CHUNK_SIZE = '256MB'
STORAGE_OPTIONS = {'config_kwargs': {'max_pool_connections': 32}, 'skip_instance_cache': True}


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

        # Example dask df with index of [0, 0, 1, 1]
        cls.example_dask_df = \
            dd.from_pandas(
                pd.concat([cls.example_df, cls.example_df], axis=0),
                npartitions=1,
                sort=False
            )
        cls.example_dask_df.to_parquet(f'{cls.test_dir.name}/dask-data.parquet')

    @classmethod
    def tearDownClass(cls):
        cls.test_dir.cleanup()

    @patch("monolith_filemanager.file.pandas_file.File.__init__")
    def test___init__(self, mock_file_init):
        PandasFile(path="test")
        mock_file_init.return_value = None
        mock_file_init.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__")
    def test_write(self, mock_init):
        mock_init.return_value = None
        test = PandasFile(path="test")

        test.path = MagicMock()
        test_data = pd.DataFrame([{"one": 1, "two": 2}, {"one": 1, "two": 2}])
        test_data_dask = dd.from_pandas(test_data, npartitions=1)

        with self.assertRaisesRegex(ValueError, 'Failed writing dataframe to file\. (.*)'):
            test.write(data=test_data, repartition=False, scheduler='test_scheduler')

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

    @patch("monolith_filemanager.file.pandas_file.PandasFile.__init__", return_value=None)
    def test_write_with_callback(self, _):
        test = PandasFile(path="test")
        cb = MagicMock()

        test.path = MagicMock()
        test_data = pd.DataFrame([{"one": 1, "two": 2}, {"one": 1, "two": 2}])
        test_data_dask = dd.from_pandas(test_data, npartitions=1)

        with self.assertRaisesRegex(ValueError, 'Failed writing dataframe to file\. (.*)'):
            test.write(data=test_data, cb=cb)

        with self.assertRaises(Exception):
            test.write(data="test")
        with self.assertRaises(Exception):
            test.write(data=1)
        with self.assertRaises(Exception):
            test.write(data=[])

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

    def test_read_dask_saved_file_eager_reset_index(self):
        """
        Dask saves partitioned dataframe folders with a different index to how pandas might store them.
        This test checks that the index returned with file.read(lazy=False) has a consistent linear index.
        """
        file = PandasFile(path=f'{self.test_dir.name}/dask-data.parquet')
        df = file.read(reset_index_if_eager=True)

        self.assertIsInstance(df, pd.DataFrame)
        assert_array_equal(df.values, self.example_dask_df.compute().values)
        assert_index_equal(df.index, pd.Index([0, 1, 2, 3]))

    def test_read_dask_saved_file_eager(self):
        """
        Dask saves partitioned dataframe folders with a different index to how pandas might store them.
        This test checks that the index returned with file.read(lazy=False) has a consistent linear index.
        """
        file = PandasFile(path=f'{self.test_dir.name}/dask-data.parquet')
        df = file.read(reset_index_if_eager=False)

        self.assertIsInstance(df, pd.DataFrame)
        assert_array_equal(df.values, self.example_dask_df.compute().values)
        assert_index_equal(df.index, pd.Index([0, 1, 0, 1]))

    def test_read_dask_saved_file_lazy_reset_index(self):
        file = PandasFile(path=f'{self.test_dir.name}/dask-data.parquet')
        df = file.read(lazy=True, reset_index_if_eager=True)

        self.assertIsInstance(df, dd.DataFrame)
        assert_frame_equal(df.compute(), self.example_dask_df.compute())

if __name__ == "__main__":
    main()
