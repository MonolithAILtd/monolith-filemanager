from typing import Any, Union

import numpy as np
import pandas as pd

from .base import File
from .errors import MatlabFileError
from ..file import FilePath


class MatlabFile(File):

    SUPPORTED_FORMATS = ["mat"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the MatlabFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)
        self._file_data = {}

    def load_bytes(self, file_path: str) -> bytes:
        """
        Load the raw data from S3 or locally.

        :param file_path: (str) full file path of data to load (e.g. './demo/Battery/mydata.mat')
        :return: (bytes) raw data bytes
        """

        # Get raw data (or filename)
        if file_path not in self._file_data:
            # real_path = dataset_manager.get_dataset_file_path(file_path)
            with open(file_path) as file:
                self._file_data[file_path] = file.read()
            return self._file_data[file_path]
        else:
            return self._file_data[file_path]

    def _load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load the data from a single file into a DataFrame.

        :param file_path: (str) full path of file
        :return: (DataFrame) by merging requested variables of the same shape
        """

        try:
            from scipy.io import loadmat, whosmat
        except ImportError:
            raise MatlabFileError(
                message="loading a matlab file relies on the scipy module. Please install this module and try again."
            )

        # Load full cycle data and get columns for each cycle
        bytes_obj = self.load_bytes(file_path)
        data = loadmat(bytes_obj)

        variables = list(data.keys())

        # Get all requested variables (names and shapes)
        whos = whosmat(bytes_obj)
        whos = [(name, shape, dtype) for name, shape, dtype in whos if name in variables]

        # Make sure there is only one unique shape for requested variables
        shapes = np.array([np.array(shape) for name, shape, dtype in whos])
        if len(np.unique(shapes, axis=0)) != 1:
            message = ", ".join([f"{name}: {shape}" for name, shape, dtype in whos])
            raise MatlabFileError(f'Unable to combine variables: {variables} due to different shapes: {message}')

        # Extract only requested keys
        df, n_rows = None, None
        for key in variables:

            # Get the variable flattened
            var = data[key].reshape(-1)

            # Make the DataFrame, if not created yet
            if df is None:
                n_rows = var.shape[0]
                df = pd.DataFrame(index=range(n_rows), columns=[])

            # Can only combine arrays of the same (flattened) shape
            if var.shape == (n_rows,):
                df[key] = var
            else:
                raise MatlabFileError(f'{key} flattened shape {var.shape} should be ({n_rows},)')

        return pd.DataFrame() if df is None else df

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the mat file
        """

        try:
            from scipy.io import loadmat
        except ImportError:
            raise MatlabFileError(
                message="loading a matlab file relies on the scipy module. Please install this module and try again."
            )

        return loadmat(self.path)

    def write(self, data: Any, **kwargs) -> None:
        raise MatlabFileError(message="write is not supported for matlab files")
