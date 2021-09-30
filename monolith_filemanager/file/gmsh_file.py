import tempfile
from typing import Any, Union

from .base import File
from .errors import GmshFileError
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

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: using tempfile as a buffer to converting a CAD file to a mesh
        """

        try:
            import gmsh
        except ImportError:
            raise GmshFileError(
                message="loading a gmsh file relies on the gmsh module. Please install this module and try again."
            )

        # if we initialize with sys.argv it could be anything
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add('Surface_Mesh_Generation')
        gmsh.open(self.path)

        # create a temporary file for the results
        out_data = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        out_data.close()

        return out_data

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (python object) data to be written to file
        :return: None
        """

        data.save(self.path)
