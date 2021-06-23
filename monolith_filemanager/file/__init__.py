from typing import Any

from ..path import FilePath
from ..singleton import Singleton
from .errors import FileMapError


class FileMap(dict, metaclass=Singleton):
    """
    This is a class for managing the imports of file types.

    Attributes:
        bindings_imported bool: False if file types have not been imported, True if they have.
    """
    bindings_imported: bool

    def __init__(self) -> None:
        """
        The constructor for the FileMap class.
        """
        super().__init__()
        self.bindings_imported = False
        self.init_bindings()

    def init_bindings(self) -> None:
        """
        Imports and loads the file objects.

        :return: None
        """
        if self.bindings_imported is False:
            from monolith_filemanager.file.gmsh_file import GmshFile
            self.add_binding(file_object=GmshFile)
            from monolith_filemanager.file.hdf5_file import Hdf5File
            self.add_binding(file_object=Hdf5File)
            from monolith_filemanager.file.json_file import JSONFile
            self.add_binding(file_object=JSONFile)
            from monolith_filemanager.file.keras_model_file import KerasModelFile
            self.add_binding(file_object=KerasModelFile)
            from monolith_filemanager.file.numpy_file import NumpyFile
            self.add_binding(file_object=NumpyFile)
            from monolith_filemanager.file.pandas_file import PandasFile
            self.add_binding(file_object=PandasFile)
            from monolith_filemanager.file.standard_pickle_file import StandardPickleFile
            self.add_binding(file_object=StandardPickleFile)
            from monolith_filemanager.file.vtk_file import VtkFile
            self.add_binding(file_object=VtkFile)
            from monolith_filemanager.file.yml_file import YmlFile
            self.add_binding(file_object=YmlFile)
            from monolith_filemanager.file.joblib_file import JoblibFile
            self.add_binding(file_object=JoblibFile)
            from monolith_filemanager.file.protobuf_file import ProtobufFile
            self.add_binding(file_object=ProtobufFile)
            from monolith_filemanager.file.matlab import MatlabFile
            self.add_binding(file_object=MatlabFile)

            self.bindings_imported = True

    def add_binding(self, file_object: Any) -> None:
        """
        Adds file object to dict.

        :param file_object: (subclass of File)
        :return: None
        """
        for key in file_object.SUPPORTED_FORMATS:
            if self.get(key, None) is not None:
                raise FileMapError(
                    message="{} for the {} class has already been defined by the {} class".format(key,
                                                                                                  file_object,
                                                                                                  self.get(key)))
            self[key] = file_object

    def get_file(self, file_path: FilePath) -> Any:
        """
        Gets file object from self.

        :param file_path: (FilePath) full path to file
        :return: file object
        """
        file_class = self.get(file_path.file_type, None)
        if file_class is None:
            raise FileMapError("{} is not in the file map".format(file_path.file_type))
        return file_class
