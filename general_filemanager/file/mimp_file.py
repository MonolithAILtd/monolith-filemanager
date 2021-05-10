from typing import Any, Union

import msgpack

from .base import File
from .errors import MimpFileError
from ..path import FilePath


class MimpFile(File):

    SUPPORTED_FORMATS = ["mimp"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the MimpFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)
        self.header = None
        self.version = None
        self.steps = None

    @staticmethod
    def format_data(data: dict) -> dict:
        """
        Makes sure that the data is in the right format.

        :param data: (dict) data to be written to mimp file format
        :return: dict in mimp file format
        """
        if not isinstance(data, dict):
            raise MimpFileError(message="{} supplied as opposed to dict".format(type(data)))
        header = data.get("header")
        if header is None:
            raise MimpFileError(message="header was not supplied")
        if header.get("version") is None:
            raise MimpFileError(message="version was not supplied in header")
        steps = data.get("steps")
        if steps is None:
            raise MimpFileError(message="steps not supplied")
        if not isinstance(steps, list):
            raise MimpFileError(message="steps should be a list instead of {}".format(type(steps)))
        for step in steps:
            if not isinstance(step, dict):
                raise MimpFileError(message="all steps need to be dicts")
        return {"header": header, "steps": steps}

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the pickle file
        """
        with open(self.path) as data_file:
            loaded_data = msgpack.unpack(data_file)
        loaded_data = self.format_data(data=loaded_data)
        self.header = loaded_data["header"]
        self.version = self.header["version"]
        self.steps = loaded_data["steps"]
        return loaded_data

    def write(self, data: Any) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """
        data = self.format_data(data=data)
        with open(self.path, 'wb') as outfile:
            msgpack.pack(data, outfile)
