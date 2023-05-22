import os
from typing import Any, Union

import cqkit
from cadquery import cq

from .base import File
from .errors import StlObjectFileError
from ..path import FilePath


class StlObjectFile(File):
    """
    This is a class for managing the reading and writing of stl objects.
    """
    SUPPORTED_FORMATS = ['stp', 'step', 'igs', 'iges']

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

        _, file_ext = os.path.splitext(self.path)
        workplane = None

        if file_ext in [".stp", ".step"]:
            # The tag can be used to identify the workplane later e.g. in error reports
            workplane = cqkit.import_step_file(self.path).tag(self.path)
        elif file_ext in [".igs", ".iges"]:
            workplane = cqkit.import_iges_file(self.path).tag(self.path)

        # This logic will only ever be exercised if the SUPPORTED_FORMATS array above is updated
        # out-of-step with any CQKit methods used in this method
        if not workplane:
            raise StlObjectFileError(f"Unsupported file type: {file_ext}")

        return workplane

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """

        data.save(self.path)
