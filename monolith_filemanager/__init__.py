from typing import Union, Optional, Any

from .path import FilePath
from .adapters.base import Base
from .adapters.s3_processes import S3ProcessesAdapter
from .adapters.local_file_processes import LocalFileProcessesAdapter
from .components.path_map import PathMap


def file_manager(file_path: Union[str, FilePath], caching: Optional[Any] = None) -> Base:
    """
    Gets the correct adapter based on the path.

    :param file_path: (str) file path
    :param caching: (Optional[Any]) the CacheManager object to be used
    :return: initialized adapter object
    """
    defined_file_path = FilePath(file_path)

    if defined_file_path.s3 is True:
        return S3ProcessesAdapter(file_path=defined_file_path, caching=caching)

    return LocalFileProcessesAdapter(file_path=defined_file_path)
