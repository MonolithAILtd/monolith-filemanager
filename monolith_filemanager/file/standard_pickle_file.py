from typing import Union

import dill as pickle
from typing import Any

from .base import File
from ..path import FilePath


class StandardPickleFile(File):
    """
    This is a class for managing the reading and writing of pickled objects in the standard way.
    """
    SUPPORTED_FORMATS = ["sav"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the StandardPickleFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: (Any) Data from the pickle file
        """
        with open(self.path, "rb") as file:
            loaded_data = pickle.load(file)
        return loaded_data

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to a pickle file.

        :param data: (python object) data to be written to file
        :return: None
        """
        with open(self.path, "wb") as file:
            pickle.dump(data, file)
