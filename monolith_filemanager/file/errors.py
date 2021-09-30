

class BaseFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PandasFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class FileMapError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MimpFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VtpFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Hdf5FileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class YamlFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class StlFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VtkFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PickleFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MatlabFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class KerasModelFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VTKFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GmshFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProtobufFileError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
