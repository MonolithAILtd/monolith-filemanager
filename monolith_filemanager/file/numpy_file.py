import numpy as np
from typing import Any, Union

from .base import File
from ..path import FilePath


class NumpyFile(File):
    """
    This is a class for managing the reading and writing of numpy objects.
    """
    SUPPORTED_FORMATS = ["npy"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the CustomDataFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the json file
        """
        return np.load(self.path)

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """

        return np.save(self.path, data, allow_pickle=False)
