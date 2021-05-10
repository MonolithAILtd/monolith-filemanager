import os
from typing import Any, Union

import tensorflow as tf

from .base import File
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
        with tf.io.gfile.GFile(self.path, "rb") as file:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(file.read())
        return graph_def

    def write(self, data: Any) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """
        directory, filename = os.path.split(self.path)
        tf.io.write_graph(
            graph_or_graph_def=data,
            logdir=directory,
            name=filename,
            as_text=False
        )
