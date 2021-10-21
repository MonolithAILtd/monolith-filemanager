from typing import Any, Union

import h5py

from .base import File
from .errors import Hdf5FileError
from ..file import FilePath


class Hdf5File(File):
    """
    This is a class for managing the reading and writing of hdf5 objects.
    """
    SUPPORTED_FORMATS = ["h5", "hdf5", "hdf"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the Hdf5File class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the hdf5 file
        """
        h5 = h5py.File(self.path, mode='r')
        return h5

    def write(self, data: Any, **kwargs) -> Exception:
        """
        Writes data to file (WARNING: not supported, raises exception).

        :param data: (python object) data to be written to file
        :return: None
        """
        raise Hdf5FileError('write method not yet implemented')
