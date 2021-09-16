from typing import Union

import dask.dataframe as dd
import pandas as pd
from dask import delayed

from .base import File
from .errors import PandasFileError
from ..path import FilePath

PandasLoadMethod = Union[pd.read_parquet, pd.read_csv, pd.read_excel, pd.read_table, pd.read_table]
DataFrameType = Union[pd.DataFrame, dd.DataFrame]


def dask_read_excel(path: str) -> dd.DataFrame:
    delayed_df = delayed(pd.read_excel)(path)
    return dd.from_delayed(delayed_df)


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
        "xls": dask_read_excel,
        "xlsx": dask_read_excel,
        "dat": dd.read_table,
        "data": dd.read_table
    }

    PANDAS_SUPPORTED_FORMATS = list(PANDAS_LOADING_METHODS)
    DASK_SUPPORTED_FORMATS = list(DASK_LOADING_METHODS)
    SUPPORTED_FORMATS = list(set(PANDAS_SUPPORTED_FORMATS + DASK_SUPPORTED_FORMATS))

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the PandasFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, lazy: bool = False, chunk_size: Union[int, str] = '64MB', **kwargs) -> DataFrameType:
        """
        Gets data from file defined by file path.

        :param lazy: (bool) Whether reading should be lazy (returns dask DataFrame) or eager (returns pandas DataFrame)
        :param chunk_size: (dask compatible int or str) size in bytes of chunks to read. Only used if lazy == True
        :return: Data from file
        """
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

        if self.path.file_type in ('xls', 'xlsx'):
            self._map_write_functions(data=data)(self.path)
        else:
            self._map_write_functions(data=data)(self.path, compute_kwargs={'scheduler': 'threads'})

    def _map_write_functions(self, data: dd.DataFrame) -> PandasLoadMethod:
        """
        Maps the write function depending on the file type from self.path (hidden file).

        :param data: (pandas data frame) data to be written to file
        :return: (PandasLoadMethod) a pandas read method ready to be used
        """
        function_map = {
            "parquet": data.to_parquet,
            "csv": data.to_csv,
            "xls": data.compute(scheduler='threads').to_excel,
            "xlsx": data.compute(scheduler='threads').to_excel,
            "dat": data.to_csv,
            "data": data.to_csv
        }
        return function_map[self.path.file_type]

    def _read_pandas(self, **kwargs) -> pd.DataFrame:
        """
        Read from file using pandas loading method

        :return: pandas DataFrame from file
        """
        if self.path.file_type not in self.PANDAS_SUPPORTED_FORMATS:
            raise PandasFileError(f'File type {self.path.file_type} not supported for eager loading.')
        return self.PANDAS_LOADING_METHODS[self.path.file_type](self.path, **kwargs)

    def _read_dask(self, chunk_size: Union[int, str], **kwargs) -> dd.DataFrame:
        """
        Read from file using dask loading method

        :param chunk_size: (int or str) dask-compatible maximum partition size. Interpreted as number of bytes.
        :return: dask DataFrame from file
        """
        if self.path.file_type not in self.DASK_SUPPORTED_FORMATS:
            raise PandasFileError(f'File type {self.path.file_type} not supported for lazy loading.')

        if self.path.file_type in ('xls', 'xlsx'):
            return self.DASK_LOADING_METHODS[self.path.file_type](self.path, **kwargs)
        elif self.path.file_type in ('parquet'):
            return self.DASK_LOADING_METHODS[self.path.file_type](self.path, chunksize=chunk_size, **kwargs)

        return self.DASK_LOADING_METHODS[self.path.file_type](self.path, blocksize=chunk_size, **kwargs)

    @staticmethod
    def supports_s3():
        return False
