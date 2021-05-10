from typing import Any, Union, Tuple, List, Optional
import shutil
from distutils.dir_util import copy_tree
import os
import glob
from datetime import datetime

from flask import send_from_directory

from monolith_filemanager.adapters.base import Base
from monolith_filemanager.path import FilePath
from monolith_filemanager.errors import FileManagerError
from monolith_filemanager.file.base import File
from .errors import LocalProcessesAdapterError


class LocalFileProcessesAdapter(Base):
    """
    This is a class for managing the interface of local file commands.

    Attributes:
        python_path (str): the path of the PYTHONPATH env variable
    """
    def __init__(self, file_path: Union[str, FilePath]) -> None:
        """
        The constructor for the LocalFileProcessesAdapter class.

        :param file_path: (str) path to the file concerned
        """
        super().__init__(file_path=file_path)
        self.python_path: str = str(os.environ.get("PYTHONPATH").split(":")[0])

    @staticmethod
    def check_local_file(path: FilePath) -> None:
        """
        Checks to see if self.path exists locally raising errors if not.

        :param path: (FilePath) the path to be checked
        :return: None
        """
        if path.root_exists is False:
            raise FileManagerError(message="root {} does not exist".format(path.root))
        elif path.file_exists is False:
            raise FileManagerError(message="file {} does not exist".format(path.file))

    def local_file_object(self) -> File:
        """
        Gets the reading and writing protocols based on the file type from the path.

        :return: (File) containing read and write protocols for the type of file
        """
        file_object = self.file_types.get_file(file_path=self.path)
        return file_object(path=self.path)

    def export_file(self):
        """
        Exports saved file.

        :return: (flask.send_from_directory) file
        """
        self.check_local_file(path=self.path)
        full_path = self.python_path + "/" + self.path.root
        return send_from_directory(directory=full_path, filename=self.path.file)

    def read_file(self, **kwargs) -> Any:
        """
        Reads file.

        :return: (Any) loaded data from the file
        """
        self.check_local_file(path=self.path)
        return self.local_file_object().read(**kwargs)

    def read_raw_file(self):
        """
        Reads file.

        :return: (bytes) loaded data from the file
        """
        self.check_local_file(path=self.path)
        with open(self.path, "rb") as f:
            return f.read()

    def custom_read_file(self, custom_read_function: Any) -> Any:
        """
        Takes a custom reading function and runs it in order to read a file based on the self.path.

        :param custom_read_function: (Any) the function that is going to read the file
        :return: (Any) the return value from the custom_read_function
        """
        self.check_local_file(path=self.path)
        return custom_read_function(self.path)

    def write_file(self, data):
        """
        Writes data to file.

        :param data: data to be written to file
        :return: None
        """
        self.create_directory_if_not_exists()
        self.local_file_object().write(data=data)

    def write_raw_file(self, data):
        """
        Writes data to file.

        :param data: data to be written to file
        :return: None
        """
        self.create_directory_if_not_exists()
        with open(self.path, "wb") as f:
            f.write(data)

    def delete_file(self, path=None):
        """
        Deletes local file.

        :return: None
        """
        if not path:
            path = self.path
        self.check_local_file(path=path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            raise FileManagerError("Could not delete folder at path: " + self.path)

    def write_stream(self, stream) -> str:
        """
        Write stream of bytes. First checks whether file name shares name of existing folder in same directory level.
        If file with same name exists already, file name is incremented before writing.
        :param stream: stream of data
        :return: (str) Name file saved as
        :raises: (LocalProcessesAdapterError) if new file name taken by existing folder
        """
        dirname = os.path.dirname(self.path)
        file_name = self.path.split("/")[-1]
        _, dirs, _ = next(os.walk(dirname))
        if self.check_name_taken(name=file_name, existing_names=dirs):
            raise LocalProcessesAdapterError("New file name already taken by folder in this folder")
        if self.exists():
            self.increment_files()

        self.create_directory_if_not_exists()
        stream.save(self.path)
        file_name = self.path.split("/")[-1]
        return file_name

    def increment_files(self) -> None:
        """
        Increments file name integer suffix based on how many files with same filename prefix exist.
        Fills in gaps in contiguous numeric sequence first. Assigns final name to self.path.
        :return: None
        """
        count = 2
        prefix = "/".join(self.path.split("/")[:-1])
        ext = os.path.splitext(self.path)[-1]
        file = ".".join(self.path.split("/")[-1].split(".")[:-1])
        new_file = prefix + "/" + file + f" {count}{ext}"
        while os.path.exists(new_file):
            count += 1
            new_file = prefix + "/" + file + f" {count}{ext}"
        self.path = new_file

    def create_directory_if_not_exists(self, increment: bool = False) -> str:
        """
        Creates a directory if it does not exist.
        :param increment: (bool) Switch for whether or not to increment file names, only use when creating only folder, no file
        :return: (str) new folder name
        :raises: (LocalProcessesAdapterError) If new folder name already taken by file in directory
        """
        dirname = os.path.dirname(self.path)
        folder = dirname.split("/")[-1]
        pardir = os.path.dirname(dirname)
        _, _, files = next(os.walk(pardir))
        if self.check_name_taken(name=folder, existing_names=files):
            raise LocalProcessesAdapterError("New folder name already taken by file in this folder")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        else:
            # handle duplicate
            if increment:
                folder = self.increment_folders(dirname=dirname)
        return folder

    @staticmethod
    def increment_folders(dirname: str) -> str:
        """
        Increment folder name suffix if name prefix already exists within parent directory.
        :param dirname: (str) folder/directory name to increment
        :return: (str) new folder name
        """
        count = 2
        prefix = "/".join(dirname.split("/")[:-1])
        folder = dirname.split("/")[-1]
        new_folder = prefix + "/" + folder + f" {count}"
        while os.path.exists(new_folder):
            count += 1
            new_folder = prefix + "/" + folder + f" {count}"
        os.makedirs(new_folder)
        return new_folder.split("/")[-1]

    def exists(self) -> bool:
        """
        Checks to see if the self.path exists

        :return: (bool) True if exists, False if not
        """
        return os.path.exists(self.path)

    def ls(self) -> Tuple[dict, List[str]]:
        """
        Lists the directories and files in a path.

        :return: (Tuple[dict, List[str]]) [file_dict, directories]
        """
        if "~" in self.path:
            self.path = os.path.expanduser(self.path)
        root, dirs, files = next(os.walk(self.path))
        file_dict = {}
        for file in files:
            last_mod, size = self._get_file_info(os.path.join(self.path, file))
            file_dict[file] = {"last_modified": last_mod, "size": size}
        return file_dict, dirs

    @staticmethod
    def _get_file_info(file: str) -> Tuple[str, int]:
        """
        Returns last modified date and file size in bytes.
        :param file: (str) local file
        :return: (Tuple[str, int]) last modified date and size in bytes
        """
        last_mod = datetime.utcfromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
        size = os.path.getsize(file)
        return last_mod, size

    def search(self, file_pattern: str) -> List[str]:
        """
        Gets paths for all files matching a glob pattern.

        :param file_pattern: (str) glob pattern of the file being searched for
        :return: list of strings which are paths to the found files
        """
        buffer: List[str] = []
        matches: List[str] = glob.glob(self.path + "/*", recursive=True)
        for path in matches:
            if file_pattern in path:
                buffer.append(path)
        return buffer

    def copy_folder(self, new_folder: str) -> None:
        """
        Copies a folder and it's contents from self.path to a path defined in the function.

        :param new_folder: (str) the folder that the self.path folder is being copied to
        :return: None
        """
        copy_tree(self.path, new_folder)

    def rename_file(self, new_name: str) -> None:
        """
        Checks file exists and new name is not already taken. Renames file according to provided arg.

        :param new_name: (str) new file name without extension
        :return: None
        :raises: (LocalProcessesAdapterError) if file doesn't exist or name already taken
        """
        pardir = os.path.dirname(self.path)
        ext = os.path.splitext(self.path)[-1]
        new_path = "/".join(self.path.split("/")[:-1]) + f"/{new_name}" + ext
        _, dirs, files = next(os.walk(pardir))
        if not self.exists():
            raise LocalProcessesAdapterError("File does not exist to rename")
        if self.check_name_taken(name=new_name, existing_names=files + dirs):
            raise LocalProcessesAdapterError("New file name already taken by a file or directory in this folder")

        os.rename(self.path, new_path)

    def rename_folder(self, new_name: str) -> None:
        """
        Checks folder exists and new name is not already taken. Renames folder according to provided arg.

        :param new_name: (str) new folder name
        :return: None
        :raises: (LocalProcessesAdapterError) if folder does not exist or new name is taken
        """
        pardir = os.path.dirname(self.path)
        new_path = "/".join(self.path.split("/")[:-1]) + f"/{new_name}"
        _, dirs, files = next(os.walk(pardir))
        if not self.exists():
            raise LocalProcessesAdapterError("Folder does not exist to rename")
        if self.check_name_taken(name=new_name, existing_names=files + dirs):
            raise LocalProcessesAdapterError("New folder name already taken by a file or directory in this folder")

        os.rename(self.path, new_path)
