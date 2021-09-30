import json
from typing import Any, Union

from monolith_filemanager.file.base import File
from ..path import FilePath


class JSONFile(File):
    """
    This is a class for managing the reading and writing of json objects.
    """
    SUPPORTED_FORMATS = ["json"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the JSONFile class.
        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the json file
        """
        with open(self.path) as data_file:
            data = json.load(data_file)
        return data

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python dict) data to be written to file
        """
        with open(self.path, 'w') as data_file:
            json.dump(data, data_file)
