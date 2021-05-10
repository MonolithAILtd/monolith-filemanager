from typing import Any, Union

from tensorflow.keras.models import save_model, load_model

from .base import File
from ..path import FilePath


class KerasModelFile(File):
    """
    This is a class for managing the reading and writing of tensorflow.keras.Model objects.
    """
    SUPPORTED_FORMATS = ["keras_model"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the KerasModelFile class.
        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, custom_objects: dict = {}, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: Data from the json file
        """
        return load_model(self.path, compile=False, custom_objects=custom_objects)

    def write(self, data: Any) -> None:
        """
        Writes data to file.
        :param data: (python dict) data to be written to file
        """
        save_model(data, self.path, include_optimizer=False, save_format='h5')
