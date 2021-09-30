from typing import Any, Union

from .base import File
from .errors import KerasModelFileError
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
        try:
            from tensorflow.keras.models import load_model
        except ImportError:
            raise KerasModelFileError(
                message="loading a keras model relies on tensorflow, to install the correct version run the command: 'file-install-tensorflow'"
            )
        return load_model(self.path, compile=False, custom_objects=custom_objects)

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.
        :param data: (python dict) data to be written to file
        """
        try:
            from tensorflow.keras.models import save_model
        except ImportError:
            raise KerasModelFileError(
                message="saving a keras model relies on tensorflow, to install the correct version run the command: 'file-install-tensorflow'"
            )
        save_model(data, self.path, include_optimizer=False, save_format='h5')
