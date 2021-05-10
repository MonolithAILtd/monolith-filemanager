import os


class FilePath(str):
    """
    This is a class for managing the path to a file.

    Attributes:
        file (str): name of file at the end of path
        file_type (str): file extension
        root (str): string leading up to the file
        s3 (bool): True if pointing to s3
    """
    def __init__(self, path: str) -> None:
        """
        The constructor for the FilePath class.

        :param path: (str) path to the file
        """
        super().__init__()
        self.file: str = path.split("/")[-1]
        self.file_type: str = self.get_file_type(file_string=self.file)
        self.root: str = "/".join(path.split("/")[0:-1]) + "/"
        self.s3: bool = self.check_if_s3(path_string=path)

    @staticmethod
    def check_if_s3(path_string: str) -> bool:
        """
        Checks to see if the path is pointing to an s3 bucket.

        :param path_string: (str) path to the file
        :return: True if s3, False if not
        """
        return path_string.startswith("s3://")

    @staticmethod
    def get_file_type(file_string: str) -> str:
        """
        Gets file extension.

        :param file_string: (str) file to be checked
        :return: (str) file extension
        """
        return file_string.split(".")[-1] if "." in file_string else None

    @property
    def root_exists(self) -> bool:
        """
        Checks to see if the root exists.

        :return: True if exists, False if not
        """
        return os.path.isdir(self.root)

    @property
    def file_exists(self) -> bool:
        """
        Checks to see if the file exists.

        :return: True if exists, False if not
        """
        return os.path.exists(self)

    def to_string(self) -> str:
        """
        Packages self to string.

        :return: (str) packaged self
        """
        return str(self)
