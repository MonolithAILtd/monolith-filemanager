import pandas as pd
from typing import Any, Union

from .base import File
from .errors import PandasFileError
from ..path import FilePath

accepted_methods = Union[pd.read_parquet, pd.read_csv, pd.read_excel, pd.read_table, pd.read_table]


class PandasFile(File):
    """
    This is a class for managing the reading and writing of data to files for pandas data frames.
    """
    LOADING_METHODS = {
        "parquet": pd.read_parquet,
        "csv": pd.read_csv,
        "xls": pd.read_excel,
        "xlsx": pd.read_excel,
        "dat": pd.read_table,
        "data": pd.read_table
    }

    SUPPORTED_FORMATS = list(LOADING_METHODS.keys())

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

    def _map_write_functions(self, data: pd.DataFrame) -> accepted_methods:
        """
        Maps the write function depending on the file type from self.path (hidden file).

        :param data: (pandas data frame) data to be written to file
        :return: (accepted_methods) a pandas read method ready to be used
        """
        function_map = {
            "parquet": data.to_parquet,
            "csv": data.to_csv,
            "xls": data.to_excel,
            "xlsx": data.to_excel,
            "dat": data.to_csv,
            "data": data.to_csv
        }
        return function_map.get(self.path.file_type)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by file path.
        
        :return: Data from file
        """
        return self.LOADING_METHODS[self.path.file_type](self.path, **kwargs)

    def write(self, data: pd.DataFrame) -> None:
        """
        Writes data to file.

        :param data: (pandas data frame) data to be written to file
        :return: None
        """
        if not isinstance(data, pd.DataFrame):
            raise PandasFileError(
                message=
                "data passed to write method isn't a pandas data frame. Please use pandas data frame for {}".format(
                    self.SUPPORTED_FORMATS
                ))
        if self.path.file_type == "parquet":
            self._map_write_functions(data=data)(self.path, index=False)
        else:
            self._map_write_functions(data=data)(self.path, header=True, index=False)

    @staticmethod
    def supports_s3():
        return False
