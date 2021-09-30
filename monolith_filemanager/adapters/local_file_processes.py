from typing import Any, Union, Tuple, List, Optional
import shutil
from distutils.dir_util import copy_tree
import os
import glob
from datetime import datetime

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
        self.python_path: str = str(os.environ.get("PYTHONPATH", "").split(":")[0])

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
        try:
            from flask import send_from_directory
        except ImportError:
            raise FileManagerError(
                message=f"exporting file relies on the Flask module. "
                        f"To install the correct version run the command: `file-install-flask`."
            )
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

    def write_file(self, data, **kwargs):
        """
        Writes data to file.

        :param data: data to be written to file
        :return: None
        """
        self._create_directory_if_not_exists()
        self.local_file_object().write(data=data, **kwargs)

    def write_raw_file(self, data):
        """
        Writes data to file.

        :param data: data to be written to file
        :return: None
        """
        self._create_directory_if_not_exists()
        with open(self.path, "wb") as f:
            f.write(data)

    def delete_file(self, path: Optional[FilePath] = None) -> None:
        """
        Deletes local file.

        :param path: (Optional[FilePath])
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
            raise FileManagerError("Could not delete file/folder at path: " + path)

    def delete_folder(self, path: Optional[FilePath] = None) -> None:
        """
        Calls delete file method which also deletes directories.

        :param path: (Optional[FilePath])
        :return: None
        """
        if not path:
            path = self.path
        self.delete_file(path=path)

    def write_stream(self, stream) -> str:
        """
        Write stream of bytes. First checks whether file name shares name of existing folder in same directory level.
        If file with same name exists already, file name is incremented before writing.
        :param stream: stream of data
        :return: (str) Name file saved as
        :raises: (LocalProcessesAdapterError) if new file name taken by existing folder
        """
        if os.path.isdir(self.path):
            raise LocalProcessesAdapterError("New file name already taken by folder in this folder")
        elif os.path.isfile(path=self.path):
            self.increment_files()

        self._create_directory_if_not_exists()
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

    def _create_directory_if_not_exists(self) -> None:
        """
        Creates a directory if it does not exist. Used privately in adapter.
        :return: None
        """
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def create_directory_if_not_exists(self) -> str:
        """
        Public method to explicitly create a directory (if it does not exist) when passed a filepath.
        :return: (str) new folder name
        :raises: (LocalProcessesAdapterError) If new folder name already taken by file in directory
        """
        dirname = FilePath(os.path.dirname(self.path))
        folder = dirname.split("/")[-1]

        if os.path.isfile(path=dirname):
            raise LocalProcessesAdapterError("New folder name already taken by file in this folder")
        elif os.path.isdir(dirname):
            folder = self.increment_folders(dirname=dirname)
        else:
            os.makedirs(dirname)
        return folder

    @staticmethod
    def increment_folders(dirname: FilePath) -> str:
        """
        Increment folder name suffix if name prefix already exists within parent directory.
        :param dirname: (FilePath) folder/directory name to increment
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

    def exists(self, path: Optional[FilePath] = None) -> bool:
        """
        Checks to see if the self.path exists

        :param path: (Optional[FilePath]) if not passed, defaults to self.path
        :return: (bool) True if exists, False if not
        """
        if not path:
            path = self.path
        return os.path.exists(path)

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
        ext = os.path.splitext(self.path)[-1]
        new_path = FilePath("/".join(self.path.split("/")[:-1]) + f"/{new_name}" + ext)
        if not self.exists():
            raise LocalProcessesAdapterError("File does not exist to rename")
        if self.exists(path=new_path):
            raise LocalProcessesAdapterError("New file name already taken by a file or directory in this folder")

        os.rename(self.path, new_path)

    def rename_folder(self, new_name: str) -> None:
        """
        Checks folder exists and new name is not already taken. Renames folder according to provided arg.

        :param new_name: (str) new folder name
        :return: None
        :raises: (LocalProcessesAdapterError) if folder does not exist or new name is taken
        """
        new_path = FilePath("/".join(self.path.split("/")[:-1]) + f"/{new_name}")
        if not self.exists():
            raise LocalProcessesAdapterError("Folder does not exist to rename")
        if self.exists(path=new_path):
            raise LocalProcessesAdapterError("New file name already taken by a file or directory in this folder")

        os.rename(self.path, new_path)

    def _move(self, new_path: FilePath) -> None:
        """
        Private method shared by both move_file and move_folder methods.
        :param new_path: (FilePath) new path to move self.path to
        :return: None
        :raises: (LocalProcessesAdapterError) if new path name already taken
        """
        if self.exists(path=new_path):
            raise LocalProcessesAdapterError("File/Folder name already taken by a file or directory in this folder")
        os.rename(self.path, new_path)

    def move_file(self, destination_folder: str) -> None:
        """
        Public move file method which formats new_path and calls _move.

        :param destination_folder: (str) folder self.path file to be moved to
        :return: None
        """
        file = self.path.split("/")[-1]
        new_path = FilePath(f"{destination_folder}/{file}")
        self._move(new_path=new_path)

    def move_folder(self, destination_folder: str) -> None:
        """
        Public move folder method which formats new_path and calls _move.

        :param destination_folder: (str) folder self.path folder to be moved to
        :return: None
        """
        folder = self.path.split("/")[-1]
        new_path = FilePath(f"{destination_folder}/{folder}")
        self._move(new_path=new_path)

    def batch_move(self, paths: List[str], destination_folder: str) -> None:
        """
        Iterates through list of paths within the self.path directory, ascertains if file or folder, then calls
        appropriate move method.

        :param paths: (List[str]) file and folder paths to be moved
        :param destination_folder: (str) folder path to be moved to
        :return: None
        """
        origin_folder = self.path
        for path in paths:
            existing_path = FilePath(f"{self.path}/{path}")
            if os.path.isfile(existing_path):
                self.path = f"{self.path}/{path}"
                self.move_file(destination_folder=destination_folder)
            else:
                self.path = f"{self.path}/{path}"
                self.move_folder(destination_folder=destination_folder)
            self.path = origin_folder
