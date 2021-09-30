import os
from typing import Any, Union

from .base import File
from .errors import ProtobufFileError
from ..path import FilePath


class ProtobufFile(File):
    """
    This is a class for managing the reading and writing of tensorflow graph objects as protobuf files.
    """
    SUPPORTED_FORMATS = ["pb"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the ProtobufFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the pb file
        """
        try:
            from tensorflow.io.gfile import GFile
            from tensorflow.compat.v1 import GraphDef
        except ImportError:
            raise ProtobufFileError(
                message="tensorflow is needed for ProtobufFile. To install run the command: 'file-install-tensorflow'"
            )
        with GFile(self.path, "rb") as file:
            graph_def = GraphDef()
            graph_def.ParseFromString(file.read())
        return graph_def

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """
        try:
            from tensorflow.io import write_graph
        except ImportError:
            raise ProtobufFileError(
                message="tensorflow is needed for ProtobufFile. To install run the command: 'file-install-tensorflow'"
            )
        directory, filename = os.path.split(self.path)
        write_graph(
            graph_or_graph_def=data,
            logdir=directory,
            name=filename,
            as_text=False
        )
