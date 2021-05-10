from typing import Any


class VersionIdentifierAdapter:
    """
    This is a class for changing the path file extension to ".sav" if the object is version controlled.

    Properties:
        cleaned_path (str): path that's modified if it's a ".pickle" file and it's version controlled
                            else => unaltered path.
    """
    def __init__(self, path: str, class_object: Any) -> None:
        """
        The constructor for the VersionIdentifierAdapter.

        :param path: (str) path to the file to be saved
        :param class_object: (Any) object to be saved
        """
        self._path: str = path
        self._class_object: Any = class_object

    @property
    def cleaned_path(self) -> str:
        """
        Alters the self._path with a ".sav" if ".pickle" is present and the object is versioned.

        :return: (str) cleaned path
        """
        if ".pickle" in self._path and (hasattr(self._class_object, "VERSION") or "VERSION" in self._class_object.__module__):
            return self._path.replace(".pickle", ".sav")
        else:
            return self._path
