from typing import Any, Union

import cqkit
from cadquery import cq

from .base import File
#from .errors import GmshFileError
from ..path import FilePath


class GmshFile(File):
    """
    This is a class for managing the reading and writing of stl objects.
    """
    SUPPORTED_FORMATS = ['brep', 'stp', 'step', 'igs', 'iges']

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the CustomDataFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> cq.Workplane:
        """
        Gets data from file defined by the file path.
        """

        # The tag can be used to identify the workplane later e.g. in error reports
        return cqkit.import_step_file(self.path).tag(self.path)

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """

        data.save(self.path)
