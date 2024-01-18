import logging
from typing import Optional, Union

import dask.dataframe as dd
import pandas as pd
from dask import delayed
from dask.callbacks import Callback

from ..path import FilePath
from .base import File
from .errors import PandasFileError

PandasLoadMethod = Union[
    pd.read_parquet, pd.read_csv, pd.read_excel, pd.read_table, pd.read_table
]
DataFrameType = Union[pd.DataFrame, dd.DataFrame]


def dask_read_excel(path: str, **kwargs) -> dd.DataFrame:
    delayed_df = delayed(pd.read_excel)(path)
    return dd.from_delayed(delayed_df)


def dask_read_xlsx(path: str, **kwargs) -> dd.DataFrame:
    delayed_df = delayed(pandas_read_xlsx)(path)
    return dd.from_delayed(delayed_df)


def pandas_read_xlsx(path: str) -> pd.DataFrame:
    # https://stackoverflow.com/questions/65250207/pandas-cannot-open-an-excel-xlsx-file
    # This is only required until we upgrade pandas to >=1.3.0, at which point openpyxl is used by
    # default for xlsx:
    # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html#pandas.read_excel
    logging.warning(f"AESC: pandas_read_xlsx({path})")
    return pd.read_excel(path, engine="openpyxl")


class PandasFile(File):
    """
    This is a class for managing the reading and writing of data to files for pandas data frames.
    """

    PANDAS_LOADING_METHODS = {
        "parquet": pd.read_parquet,
        "csv": pd.read_csv,
        "xls": pd.read_excel,
        "xlsx": pandas_read_xlsx,
        "dat": pd.read_table,
        "data": pd.read_table,
    }

    DASK_LOADING_METHODS = {
        "parquet": dd.read_parquet,
        "csv": dd.read_csv,
        "xls": dask_read_excel,
        "xlsx": dask_read_xlsx,
        "dat": dd.read_table,
        "data": dd.read_table,
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

    def read(
        self,
        lazy: bool = False,
        chunk_size: Union[int, str] = "256MB",
        reset_index_if_eager: bool = True,
        **kwargs,
    ) -> DataFrameType:
        """
        Gets data from file defined by file path.
        If `lazy` is True, then returns a Dask DataFrame.
        If `lazy` is False, then returns a Pandas DataFrame. The index can be reset to avoid inconsistency with how Dask
            stores DataFrame indexes.

        :param lazy: (bool) Whether reading should be lazy (returns dask DataFrame) or eager (returns pandas DataFrame)
        :param chunk_size: (dask compatible int or str) size in bytes of chunks to read. Only used if lazy == True
        :param reset_index_if_eager: (bool) Whether or not to reset the index of the read dataframe.
            Only resets the index of pandas dataframes
        :return: (DataFrameType) Data from file
        """
        storage_options = {
            "config_kwargs": {"max_pool_connections": 32},
            "skip_instance_cache": True,
        }


        row_start = kwargs.get('row_start',None)
        row_end = kwargs.get('row_end',None)
        if row_start and row_end:
            df = self._partial_read_pandas(row_start, row_end)
        else:
            df = (
                self._read_dask(chunk_size, storage_options=storage_options, **kwargs)
                if lazy
                else self._read_dask(
                    chunk_size, storage_options=storage_options, **kwargs
                ).compute()
            )

            if reset_index_if_eager and not lazy:
                # Reset the index of pandas dataframes if requested
                df = df.reset_index(drop=True)

        return df

    def write(
        self,
        data: DataFrameType,
        repartition: bool = False,
        divisions: Union[int, str] = "64MB",
        scheduler: str = "threads",
        cb: Optional[Callback] = None,
        **kwargs,
    ) -> None:
        """
        Writes data to file.

        :param data: (pandas or dask data frame) data to be written to file
        :param repartition: (bool) whether or not to repartition the dataframe to a given chunk size. Default to False.
        :param divisions: (list of int, or int or str) dask-compatible maximum partition size.
                                    Interpreted as index of partitions if a list of ints
                                    Interpreted as number of bytes if str,
                                    Interpreted as number of divisions if int.
        :param scheduler: (str) Dask local scheduler type to use for computation.
            Choose from "threads", "single-threaded", or "processes"
        :param cb: (optional dask Callback) A dask-compatible callback for updates during computation of the dask graph.
        :return: None
        """

        if not isinstance(data, (pd.DataFrame, dd.DataFrame)):
            raise PandasFileError(
                message=f"Data passed to write method isn't a pandas or dask DataFrame. "
                f"Please use a DataFrame for {self.DASK_SUPPORTED_FORMATS}"
            )

        if isinstance(data, pd.DataFrame):
            data = dd.from_pandas(data, npartitions=1, sort=False)

        if repartition:
            data = data.repartition(divisions=divisions)

        if cb is None:
            self._write_functions(data, self.path, scheduler)
        else:
            with cb:
                self._write_functions(data, self.path, scheduler)

    @staticmethod
    def _write_functions(df: DataFrameType, path: FilePath, scheduler: str) -> None:
        """
        Function for mapping file type to correct write method.

        :param df: (pandas or dask data frame) data to be written to file
        :param path: (FilePath) the path to save the dataframe to.
        :param scheduler: (str) Dask local scheduler type to use for computation.
            Choose from "threads", "single-threaded", or "processes"
        """
        if path.file_type in ("xls", "xlsx"):
            df.compute(scheduler=scheduler).to_excel(path),
        elif path.file_type in ("csv", "dat", "data"):
            df.to_csv(path, compute_kwargs={"scheduler": scheduler}, single_file=True)
        elif path.file_type in ("parquet",):
            df.to_parquet(path, compute_kwargs={"scheduler": scheduler})
        else:
            raise ValueError(
                f"Failed writing dataframe to file. File type {path.file_type} not known."
            )

    def _read_dask(self, chunk_size: Union[int, str], **kwargs) -> dd.DataFrame:
        """
        Read from file using dask loading method

        :param chunk_size: (int or str) dask-compatible maximum partition size. Interpreted as number of bytes.
        :return: dask DataFrame from file
        """
        if self.path.file_type not in self.DASK_SUPPORTED_FORMATS:
            raise PandasFileError(
                f"File type {self.path.file_type} not supported for lazy loading."
            )

        if self.path.file_type in ("xls", "xlsx"):
            return self.DASK_LOADING_METHODS[self.path.file_type](self.path, **kwargs)
        elif self.path.file_type in ("parquet",):
            return self.DASK_LOADING_METHODS[self.path.file_type](
                self.path, chunksize=chunk_size, **kwargs
            )

        return self.DASK_LOADING_METHODS[self.path.file_type](
            self.path, blocksize=chunk_size, **kwargs
        )

    def _partial_read_pandas(self, row_start: int, row_end: int) -> pd.DataFrame:
        """
        Read from file using pandas loading method for reading between row_start and row_end

        :param chunk_size: (int or str) dask-compatible maximum partition size. Interpreted as number of bytes.
        :return: dask DataFrame from file
        """
        if self.path.file_type not in self.PANDAS_SUPPORTED_FORMATS:
            raise PandasFileError(
                f"File type {self.path.file_type} not supported by pandas."
            )

        skip_rows = max(row_start - 1, 0)  # Adjust for zero-based index
        nrows = row_end - row_start
        return self.PANDAS_LOADING_METHODS[self.path.file_type](
            self.path, skiprows=skip_rows, nrows=nrows
        )

    @staticmethod
    def supports_s3():
        return True
