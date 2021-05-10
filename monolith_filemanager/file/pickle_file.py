from typing import Any, Union

from .base import File
from .errors import PickleFileError
from ..path import FilePath


class PickleFile(File):
    """
    This is a class for managing the reading and writing of pickled objects.
    """
    SUPPORTED_FORMATS = ["pickle"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the PickleFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: (Any) Data from the pickle file
        """
        try:
            from pickle_factory import base as pickle_factory
        except ImportError:
            raise PickleFileError(
                "You are trying to read a legacy DPU object without the "
                "pickle_factory plugin. You need the pickle_factory directory in your "
                "PYTHONPATH")
        raw_data = open(self.path, 'rb')
        loaded_data = pickle_factory.load(file=raw_data)
        raw_data.close()
        return loaded_data

    def write(self, data: Any) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """
        try:
            from pickle_factory import base as pickle_factory
        except ImportError:
            raise PickleFileError(
                "You are trying to read a legacy DPU object without the "
                "pickle_factory plugin. You need the pickle_factory directory in your "
                "PYTHONPATH")
        file = open(self.path, 'wb')
        pickle_factory.dump(obj=data, file=file)
