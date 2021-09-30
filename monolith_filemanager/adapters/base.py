from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Union, Optional

from monolith_filemanager.file import FileMap
from monolith_filemanager.path import FilePath


class Base(ABC):
    """
    This is a class for managing the base functions for other adapters.

    Attributes:
        path (FilePath): the full path to the file (FilePath is defined in the file_manager_factory)
        file_types (FileMap: dict): dictionary of the different file types with read and write functionality
        config (Optional[str]): configuration for the adapter
    """
    def __init__(self, file_path: Union[FilePath]) -> None:
        """
        The constructor for the Base class.

        :param file_path: (FilePath) the full path to the file (FilePath is defined in the file_manager_factory)
        """
        self.path: FilePath = file_path
        self.file_types: FileMap = FileMap()
        self._s3: bool = False
        self.config: Optional[str] = None

    def define_config(self, config: str) -> None:
        """
        Defines the config attribute.

        :param config: (str) the configuration dictionary that is attached to the self.config attribute
        :return: None
        """
        self.config = config

    @abstractmethod
    def read_file(self, **kwargs) -> Any:
        """
        Placeholder for reading from file

        :return: data from file
        """
        pass

    @abstractmethod
    def read_raw_file(self) -> bytes:
        """
        Placeholder for reading raw data from file

        :return: (bytes) data from file
        """
        pass

    @abstractmethod
    def custom_read_file(self, custom_read_function) -> Any:
        pass

    @abstractmethod
    def write_file(self, data, **kwargs) -> None:
        """
        Placeholder for writing data to a file.

        :param data: data that has to be written to a file
        :return: None
        """
        pass

    @abstractmethod
    def write_raw_file(self, data: bytes) -> None:
        """
        Placeholder for writing raw data to a file.

        :param data: data that has to be written to a file
        :return: None
        """
        pass

    @abstractmethod
    def delete_file(self, path=None) -> None:
        pass

    @abstractmethod
    def delete_folder(self, path=None) -> None:
        pass

    @abstractmethod
    def write_stream(self, stream) -> None:
        pass

    @abstractmethod
    def create_directory_if_not_exists(self) -> None:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def ls(self) -> Tuple[List[str], List[str]]:
        """
        Placeholder for returning list of files and subdirectories.

        :return: Tuple of list of subdirectories and list of files within folder
        """
        pass

    @abstractmethod
    def copy_folder(self, new_folder: str) -> None:
        pass

    def batch_delete(self, paths: List[str]) -> None:
        """
        Batch delete files or folders within the parent directory of self.path.

        :param paths: (List[str]) file/folder paths within self.path to be deleted
        :return: None
        """
        for path in paths:
            del_path = FilePath(f"{self.path}/{path}")
            self.delete_file(path=del_path)

    @abstractmethod
    def rename_file(self, new_name: str) -> None:
        pass

    @abstractmethod
    def rename_folder(self, new_name: str) -> None:
        pass

    @abstractmethod
    def move_file(self, destination_folder: str) -> None:
        pass

    @abstractmethod
    def move_folder(self, destination_folder: str) -> None:
        pass
