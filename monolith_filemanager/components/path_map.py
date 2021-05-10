from typing import Dict, List, Union

from ..path import FilePath


class PathMap(dict):
    """
    This class is responsible for mapping the root of a path to another path.
    """
    def __init__(self, file_map: Dict) -> None:
        """
        The constructor for the PathMap class.

        :param file_map: (Dict) config dictionary to act as a map
        """
        super().__init__(file_map)

    def map_path(self, path: Union[FilePath, str]) -> FilePath:
        """
        Maps the path to the path defined in the config.

        :param path: (Union[FilePath, str]) path to be mapped
        :return: (FilePath) path that has been rerouted
        """
        buffer: List[str] = path.split("/")

        if self.get(buffer[0]) is not None:
            buffer[0] = self[buffer[0]]

        return FilePath("/".join(buffer))
