from typing import Union, Any

import numpy as np

from .base import File
from .errors import VTKFileError
from ..path import FilePath


class VtkFile(File):
    """
    This is a class for managing the reading and writing of vtp files.
    """
    SUPPORTED_FORMATS = ["obj", "ply", "stl", "vtk", "vtp", "vtu"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the VtpFile class.
        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Any:
        """
        Gets data from file defined by the file path.

        :return: (Any) data from file
        """
        try:
            from pyvista import read as pv_read
        except ImportError:
            raise VTKFileError(
                message="loading a vtk file relies on the vtk module. Please install this module and try again."
            )

        return expand_3d_point_arrays(pv_read(self.path))

    def write(self, data: Any, **kwargs) -> None:
        """
        Writes data to file.
        :param data: (python object) data to be written to file
        :return: None
        """
        data.save(self.path)


def expand_3d_point_arrays(mesh):
    """
    Helper function for expanding 3D point surfaces into 1D point surfaces and a magnitude vector.
    @param mesh:  (pv.PolyData) input mesh to expand
    @return: (pv.PolyData) mesh with expanded point surfaces
    """
    if all(arr.shape[-1] == 1 for arr in mesh.point_arrays.values()):
        return mesh

    new_mesh = mesh.copy()
    new_mesh.clear_point_arrays()

    for key, arr in mesh.point_arrays.items():
        if arr.shape[-1] == 3:
            new_mesh.point_arrays.update({f'{key}:X': arr[:, 0],
                                          f'{key}:Y': arr[:, 1],
                                          f'{key}:Z': arr[:, 2],
                                          f'{key}:Magnitude': np.linalg.norm(arr, axis=1),
                                          })
        else:
            new_mesh.point_arrays[key] = arr

    return new_mesh
