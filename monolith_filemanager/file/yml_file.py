from typing import Dict, Union

import yaml

from .base import File
from .errors import YamlFileError
from ..path import FilePath


class YmlFile(File):
    """
    This is a class for managing the reading and writing of yaml files.
    """
    SUPPORTED_FORMATS = ["yml"]

    def __init__(self, path: Union[str, FilePath]) -> None:
        """
        The constructor for the YmlFile class.

        :param path: (str/FilePath) path to the file
        """
        super().__init__(path=path)

    def read(self, **kwargs) -> Dict:
        """
        Gets data from file defined by the file path.

        :return: Data from the yaml file
        """
        yml_path = str.encode(self.path)
        raw_data = open(yml_path, 'rb')
        loaded_data = yaml.load(raw_data, Loader=yaml.FullLoader)
        raw_data.close()
        return loaded_data

    def write(self, data: Dict, **kwargs) -> None:
        """
        Writes data to file.

        :param data: (dict) data to be written to file
        :return: None
        """
        if not isinstance(data, dict):
            raise YamlFileError(message="{} data supplied instead of dict".format(type(data)))
        yml_path = str.encode(self.path)
        file = open(yml_path, 'w')
        yaml.dump(data, file)
        file.close()
