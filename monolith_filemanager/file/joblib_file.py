import joblib
from typing import Any, Union

from monolith_filemanager.file.base import File
from ..path import FilePath


class JoblibFile(File):
    """
    This is a class for managing the reading and writing of joblib objects.
    """
    SUPPORTED_FORMATS = ["joblib"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the JoblibFile class.
        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the joblib file
        """
        return joblib.load(self.path)

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python dict) data to be written to file
        """
        joblib.dump(data, self.path)
