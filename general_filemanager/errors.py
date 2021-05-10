

class FilePathError(Exception):

    def __init__(self, message: str) -> None:
        """
        The constructor for the FilePathError class.

        :param message: (str) the message in which the error is raised under
        """
        super().__init__(message)


class FileManagerError(Exception):

    def __init__(self, message: str) -> None:
        """
        The constructor for the FileManagerError class.

        :param message: (str) the message in which the error is raised under
        """
        super().__init__(message)


class PathMapError(Exception):

    def __init__(self, message: str) -> None:
        """
        The constructor for the PathMapError class.

        :param message: (str) the message in which the error is raised under
        """
        super().__init__(message)
