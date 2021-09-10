from typing import Union

import dask.dataframe as dd
import pandas as pd

from .base import File
from .errors import PandasFileError
from ..path import FilePath

accepted_methods = Union[pd.read_parquet, pd.read_csv, pd.read_excel, pd.read_table, pd.read_table]
DataFrameType = Union[pd.DataFrame, dd.DataFrame]


class PandasFile(File):
    """
    This is a class for managing the reading and writing of data to files for pandas data frames.
    """
    PANDAS_LOADING_METHODS = {
        "parquet": pd.read_parquet,
        "csv": pd.read_csv,
        "xls": pd.read_excel,
        "xlsx": pd.read_excel,
        "dat": pd.read_table,
        "data": pd.read_table
    }

    DASK_LOADING_METHODS = {
        "parquet": dd.read_parquet,
        "csv": dd.read_csv,
        # TODO find a way to read excel files with dask. Possibly with dask delayed and pandas read_csv
        # "xls": dd.read_excel,
        # "xlsx": dd.read_excel,
        "dat": dd.read_table,
        "data": dd.read_table
    }

    PANDAS_SUPPORTED_FORMATS = list(PANDAS_LOADING_METHODS)
    DASK_SUPPORTED_FORMATS = list(DASK_LOADING_METHODS)
    SUPPORTED_FORMATS = list(set(PANDAS_SUPPORTED_FORMATS + DASK_SUPPORTED_FORMATS))

    LOADING_KWARGS = {
        "dat": {"sep": "\s+"},
        "data": {"sep": "\s+"}
    }

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the PandasFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, lazy: bool = False, chunk_size: Union[int, str] = '64MB', **kwargs) -> DataFrameType:
        """
        Gets data from file defined by file path.
        
        :return: Data from file
        """
        # TODO do such that if dask or pandas can't handle, the other one can
        return self._read_dask(chunk_size, **kwargs) if lazy else self._read_pandas(**kwargs)

    def write(self, data: DataFrameType, chunk_size: Union[int, str] = '64MB') -> None:
        """
        Writes data to file.

        :param data: (pandas or dask data frame) data to be written to file
        :param chunk_size: (int or str) dask-compatible maximum partition size. Interpreted as number of bytes.
        :return: None
        """
        if not isinstance(data, (pd.DataFrame, dd.DataFrame)):
            raise PandasFileError(message=f'Data passed to write method isn\'t a pandas or dask DataFrame. '
                                          f'Please use a DataFrame for {self.DASK_SUPPORTED_FORMATS}')

        if isinstance(data, pd.DataFrame):
            data = dd.from_pandas(data, npartitions=1)

        data = data.repartition(partition_size=chunk_size)
        self._map_write_functions(data=data)(self.path, compute_kwargs={'scheduler': 'threads'})

    def _map_write_functions(self, data: DataFrameType) -> accepted_methods:
        """
        Maps the write function depending on the file type from self.path (hidden file).

        :param data: (pandas data frame) data to be written to file
        :return: (accepted_methods) a pandas read method ready to be used
        """
        function_map = {
            "parquet": data.to_parquet,
            "csv": data.to_csv,
            # "xls": data.to_excel,
            # "xlsx": data.to_excel,
            "dat": data.to_csv,
            "data": data.to_csv
        }
        return function_map[self.path.file_type]

    def _read_pandas(self, **kwargs) -> pd.DataFrame:
        if self.path.file_type not in self.PANDAS_SUPPORTED_FORMATS:
            raise PandasFileError(f'File type {self.path.file_type} not supported for eager loading.')
        return self.PANDAS_LOADING_METHODS[self.path.file_type](self.path, **kwargs)

    def _read_dask(self, chunk_size: Union[int, str], **kwargs) -> dd.DataFrame:
        if self.path.file_type not in self.DASK_SUPPORTED_FORMATS:
            raise PandasFileError(f'File type {self.path.file_type} not supported for lazy loading.')

        # Set both chunksize and block_size kwargs as depending on dask read method can use either
        return self.DASK_LOADING_METHODS[self.path.file_type](self.path, chunksize=chunk_size, block_size=chunk_size,
                                                              **kwargs)

    @staticmethod
    def supports_s3():
        return False
