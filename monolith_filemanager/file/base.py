from abc import ABC, abstractmethod
from typing import Union

from .errors import BaseFileError
from ..path import FilePath


class File(ABC):
    """
    This is a class for managing the base attributes of a file class.

    Attributes:
        path (FilePath): path to file
    """
    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the File base path.

        :param path: (str/FilePath) path to file
        """
        if isinstance(path, FilePath):
            self.path: FilePath = path
        elif isinstance(path, str):
            self.path: FilePath = FilePath(path)
        else:
            raise BaseFileError("{} cannot be configured into a path, please pass FilePath object or string".format(
                path))

    @abstractmethod
    def read(self, **kwargs) -> None:
        pass

    @abstractmethod
    def write(self, data, **kwargs) -> None:
        pass

    @staticmethod
    def supports_s3() -> bool:
        return False
