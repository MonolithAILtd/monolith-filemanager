import os
import pathlib
from typing import Tuple, List, Union

import yaml
import requests


def get_latest_version_number() -> str:
    """
    Gets the latest pip version number from the pypi server.

    Returns: (str) the version of the latest pip module
    """
    req = requests.get("https://pypi.org/pypi/monolith-filemanager/json")
    return req.json()["info"]["version"]


def write_version_to_file(version_number: str) -> None:
    """
    Writes the version to the VERSION.py file.

    Args:
        version_number: (str) the version to be written to the file

    Returns: None
    """
    version_file_path: str = str(pathlib.Path(__file__).parent.absolute()) + "/monolith_filemanager/version.py"

    if os.path.exists(version_file_path):
        os.remove(version_file_path)
    print(f"version number: {version_number}")
    with open(version_file_path, "w") as f:
        f.write(f"VERSION='{version_number}'")


def unpack_version_number(version_string: str) -> Tuple[int, int, int]:
    """
    Unpacks the version number converting it into a Tuple of integers.

    Args:
        version_string: (str) the version to be unpacked

    Returns: (Tuple[int, int, int]) the version number
    """
    version_buffer: List[str] = version_string.split(".")
    return int(version_buffer[0]), int(version_buffer[1]), int(version_buffer[2])


def pack_version_number(version_buffer: Union[Tuple[int, int, int], List[int]]) -> str:
    """
    Packs the version number into a string.

    Args:
        version_buffer: (Union[Tuple[int, int, int], List[int]]) the version to be packed

    Returns: (str) the packed version number
    """
    return f"{version_buffer[0]}.{version_buffer[1]}.{version_buffer[2]}"


def increase_version_number(version_buffer: Union[Tuple[int, int, int], List[int]], semantic_version: str = "patch") -> List[int]:
    """
    Increases the number of the version based on the 'release_type' value in the release_type.yaml

    Args:
        version_buffer: (Union[Tuple[int, int, int], List[int]]) the version to be increased
        semantic_version: (str) the semantic version/release type e.g. patch, minor, major, defaults to patch
                            if not recognised

    Returns: (List[int]) the updated version
    """
    first: int = version_buffer[0]
    second: int = version_buffer[1]
    third: int = version_buffer[2]

    if semantic_version == "patch":
        third += 1
    elif semantic_version == "minor":
        second += 1
        third = 0
    elif semantic_version == "major":
        first += 1
        second = 0
        third = 0
    else:
        third += 1

    return [first, second, third]


def determine_release_type() -> str:
    """
    Read the 'release_type.yaml' file and parse for the 'release_type' key value. This should be amended accordingly
    by the developer depending on the nature of the latest changes.
    """
    yml_path = str.encode(str(pathlib.Path(__file__).parent.absolute()) + "/release_type.yaml")
    raw_data = open(yml_path, 'rb')
    loaded_data = yaml.load(raw_data, Loader=yaml.FullLoader)
    raw_data.close()
    return loaded_data['release_type']


if __name__ == "__main__":
    release_type = determine_release_type()
    write_version_to_file(
        version_number=pack_version_number(
            version_buffer=increase_version_number(
                version_buffer=unpack_version_number(
                    version_string=get_latest_version_number()
                ), semantic_version=release_type
            )
        )
    )
