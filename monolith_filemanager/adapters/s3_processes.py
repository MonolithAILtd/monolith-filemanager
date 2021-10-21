import posixpath
from typing import Any, Union, Tuple, List, Optional
from urllib.parse import unquote

import globre

from monolith_filemanager.adapters.base import Base
from monolith_filemanager.adapters.errors import S3ProcessesAdapterError
from monolith_filemanager.file.base import File, FilePath
from monolith_filemanager.s3storage import V1Engine


class S3ProcessesAdapter(Base):
    """
    This is a class for managing the interface of s3 file commands.
    """
    def __init__(self, file_path: Union[FilePath], caching: Optional[Any] = None) -> None:
        """
        The constructor for the S3ProcessesAdapter class.

        self.path has any trailing '/' stripped to account for root folder level paths e.g. s3://example-bucket/

        :param file_path: (str) path to the file concerned
        :param caching: (Optional[Any]) the CacheManager object to be used which is to be initialized before being passed through
        """
        super().__init__(file_path=file_path)
        self._engine: V1Engine = V1Engine()
        self._cache: Any = caching
        self._s3: bool = True
        self._strip_path_slash()

    def local_file_object(self) -> File:
        """
        Gets the reading and writing protocols based on the file type from the path.

        :return: Object containing read and write protocols for the type of file
        """
        file_object = self.file_types.get_file(file_path=self.path)
        return file_object(path=self.path)

    def read_file(self, **kwargs) -> Any:
        """
        Reads file from s3 storage.

        :return: data from file
        """
        if self.path.file_type == "pickle":
            try:
                from pickle_factory import base as pickle_factory
            except ImportError:
                raise S3ProcessesAdapterError(
                    message="you are trying to read a .pickle file without the legacy DPU pickle_factory plugin. "
                            "If you are not trying to pickle a DPU legacy object please use .sav instead of .pickle. "
                            "If you are trying to process DPU legacy objects please define the pickle_factory "
                            "in your PYTHONPATH")
            raw_data = self._engine.download_raw_data_file(storage_path=self.path.to_string())
            return pickle_factory.load(file=raw_data, memory=True)

        elif self.path.file_type == "parquet":
            # read_parquet can support s3 paths
            return self.local_file_object().read(**kwargs)

        else:
            if self._cache is None:
                self.raise_missing_cache_error(usage=f'read file \'{self.path}\'')
            self._cache.create_cache()
            stored_file_path = self._engine.download_data_file(storage_path=self.path.to_string(),
                                                               file_path=self._cache.cache_path)
            self.path = FilePath(stored_file_path)
            return self.local_file_object().read(**kwargs)

    def read_raw_file(self) -> Any:
        """
        Reads raw file from s3 storage.

        :return: (bytes) data from file
        """
        return self._engine.download_raw_data_file(storage_path=self.path.to_string())

    def custom_read_file(self, custom_read_function: Any) -> Any:
        """
        Passes a custom function and executes it in order to read the data.

        :param custom_read_function:
        :return:
        """
        if self._cache is None:
            self.raise_missing_cache_error(usage=f'custom read file \'{self.path}\'')
        self._cache.create_cache()
        stored_file_path = self._engine.download_data_file(storage_path=self.path,
                                                           file_path=self._cache.cache_path)
        self.path = stored_file_path
        return custom_read_function(self.path)

    def raise_missing_cache_error(self, usage: str):
        """
        Raise an error that the caching module is required but not provided.
        :param usage: (str) message about the task that was being attempted.
        :return: None
        """
        raise S3ProcessesAdapterError(
            f'You are trying to {usage} without providing a CacheManager object from the caching module. '
            f'Try the following:\n'
            '1) pip install the Monolith caching module;\n'
            '2) Create file objects passing an instance of `caching.CacheManager()` to `file_manager` method;\n'
            'For example:'
            '`file = general_filemanager.file_manager(file_path=file_path, caching=caching.CacheManager())`'
        )

    def write_file(self, data: Any, **kwargs) -> None:
        """
        Uploads data to s3 bucket.

        :param data: (Any) data to be uploaded to bucket
        :return: None
        """
        file_object = self.local_file_object()
        if file_object.supports_s3():
            return file_object.write(data, **kwargs)
        else:
            if self._cache is None:
                self.raise_missing_cache_error(usage=f'write file \'{self.path}\'')
            self._cache.create_cache()
            file_object.path = FilePath(self._cache.cache_path + file_object.path.split("/")[-1])
            file_object.write(data)
            self._engine.upload_data_from_file(storage_path=self.path.to_string(), file_path=file_object.path.to_string())

    def write_raw_file(self, data: Any) -> None:
        """
        Uploads raw data to s3 bucket directly.

        :param data: (Any) data to be uploaded to bucket
        :return: None
        """
        self._engine.upload_data(storage_path=self.path.to_string(), data=data)

    def delete_file(self, path: Optional[FilePath] = None) -> None:
        """
        Deletes file data from s3 bucket.

        :param path: (Optional[FilePath]) if None, defaults to self.path
        :return: None
        """
        if not path:
            path = self.path
        self._engine.delete(storage_path=path)

    def delete_folder(self, path: Optional[FilePath] = None) -> None:
        """
        Deletes "folder" and contents from s3 bucket.

        :param path: (Optional[FilePath]) if None, defaults to self.path
        :return: None
        """
        if not path:
            path = self.path
        bucket, folder_name, short_file_name = V1Engine._split_s3_path(storage_path=path)
        # ensure folder names being passed as s3 "Prefix" args are terminated with a "/"
        self._engine.delete_file(bucket_name=bucket, file_name=f"{folder_name}/")

    def write_stream(self, stream: Any) -> str:
        """
        Writes a stream of data to a cache and then uploads it to a s3 path.
        Checks that filename for path is not already taken by folder in the parent directory.
        If file with name already exists, name is incremented.

        :param stream: (Any) the stream to be written
        :return: (str) Name file saved as
        :raises: (S3ProcessesAdapterError) If file name already used by existing folder parent directory
        """
        if self._cache is None:
            self.raise_missing_cache_error(usage=f'write stream \'{self.path}\'')
        self._cache.create_cache()
        file_name = self.path.split("/")[-1]
        file_path = self._cache.cache_path + file_name
        parent_dir = FilePath("/".join(self.path.split("/")[:-1]) + "/")
        stream.save(file_path)
        files, dirs = self.ls(path=parent_dir)
        if self.check_name_taken(file_name, dirs):
            raise S3ProcessesAdapterError("New file name already taken by folder in this folder")
        if self.exists():
            self.increment_files()

        self._engine.upload_data_from_file(storage_path=self.path, file_path=file_path)
        file_name = self.path.split("/")[-1]
        return file_name

    def increment_files(self) -> None:
        """
        Increments file name integer suffix based on how many files with same filename prefix exist within S3 folder obj.
        Fills in gaps in contiguous numeric sequence first. Assigns final name to self.path.
        :return: None
        """
        count = 2
        prefix = "/".join(self.path.split("/")[:-1])
        ext = f".{self.path.split('.')[-1]}"
        file = ".".join(self.path.split("/")[-1].split(".")[:-1])
        new_file = FilePath(prefix + "/" + file + f" {count}{ext}")
        while self.exists(path=new_file):
            count += 1
            new_file = FilePath(prefix + "/" + file + f" {count}{ext}")
        self.path = new_file

    def create_directory_if_not_exists(self) -> str:
        """
        Creates a directory if it does not exist.
        :return: (str) returns name of newly created folder
        """
        return self._engine.create_folder(storage_path=self.path)

    def exists(self, path: Optional[FilePath] = None) -> bool:
        """
        Checks to see if the self.path exists.

        :return: (bool) True if exists, False if not
        """
        if path:
            return self._engine.exists(storage_path=path)
        else:
            return self._engine.exists(storage_path=self.path)

    def ls(self, path: Optional[FilePath] = None) -> Tuple[dict, List[str]]:
        """
        Lists all the sub directories and sub files belonging to the self.path.

        :param path: (Optional[str]) directory path if different from self.path
        :return: (Tuple[dict, List[str]]) sub files and sub directories
        """
        if path:
            return self._engine.ls(storage_path=path)
        else:
            return self._engine.ls(storage_path=self.path.to_string())

    def _extract_info(self, path: str) -> Tuple[str, str, str]:
        bucket_name = self.config[5:].split("/")[0]
        base_prefix = self.config[5 + len(bucket_name) + 1:]
        prefix = path[2:]
        if len(base_prefix) > 0:
            prefix = posixpath.join(base_prefix, prefix)
        return bucket_name, base_prefix, prefix

    def search(self, file_pattern: str) -> List[str]:
        """
        Gets paths for all files matching a glob pattern.

        :param file_pattern: (str) glob pattern of the file being searched for
        :return: list of strings which are paths to the found files
        """
        bucket_name, base_prefix, prefix = self._extract_info(self.path)
        bucket = self._engine.resource.Bucket(bucket_name)
        if len(prefix) > 0 and not prefix.endswith("/"):
            prefix = prefix + "/"
        all_objects = bucket.objects.filter(Prefix=prefix)
        if len(prefix) > 0:
            file_pattern = posixpath.join(prefix, file_pattern)
        all_files = [obj.key for obj in all_objects]
        return [posixpath.join("./", posixpath.relpath(self._clean_name(file), base_prefix)) for file in all_files if
                self._glob_match(file_pattern, self._clean_name(file))]

    def copy_file(self, new_path: FilePath) -> None:
        """
        Copies self.path file to a new file path.

        :param new_path: (FilePath) destination path for file to be copied to
        :return: None
        """
        old_bucket_name, old_file_name, _ = self._engine._split_s3_path(self.path)
        new_bucket_name, new_file_name, _ = self._engine._split_s3_path(new_path)

        self._engine.resource.Object(new_bucket_name, new_file_name).copy_from(
            CopySource=f"{old_bucket_name}/{old_file_name}")

    def copy_folder(self, new_folder: str) -> None:
        """
        Copies one folder to another folder.

        :param new_folder: (str) the directory to where the folder will be copied to
        :return: None
        """
        old_bucket_name, old_folder_name, _ = self._engine._split_s3_path(self.path)
        new_bucket_name, new_folder_name, _ = self._engine._split_s3_path(new_folder)

        old_bucket = self._engine.resource.Bucket(old_bucket_name)
        new_bucket = self._engine.resource.Bucket(new_bucket_name)

        for obj in old_bucket.objects.filter(Prefix=f"{old_folder_name}/"):
            old_source = {'Bucket': old_bucket_name,
                          'Key': obj.key}

            new_key = obj.key.replace(old_folder_name, new_folder_name, 1)
            new_obj = new_bucket.Object(new_key)
            new_obj.copy(old_source)

    @staticmethod
    def _split_s3_path(storage_path: Union[FilePath, str]) -> Tuple[str, str, str]:
        """
        Splits the path into bucket, file name, and short_file_name.

        :param storage_path: (Union[FilePath, str]) path to be split
        :return: (Tuple[str, str, str]) bucket_name, file_name, short_file_name
        """
        path = storage_path.replace("s3://", "")
        path = path.split("/")
        bucket_name = path[0]
        file_name = "/".join(path[1:])
        short_file_name = path[-1]
        return bucket_name, file_name, short_file_name

    @staticmethod
    def _clean_name(text: str) -> str:
        """
        Cleans the string from quotes.

        :param text: (str) string to be cleaned
        :return: (str) cleaned string
        """
        res = unquote(text)
        return res

    @staticmethod
    def _glob_match(pattern: str, file: str):
        return bool(globre.match(pattern, file))

    def rename_file(self, new_name: str) -> None:
        """
        Checks file to rename exists, checks new name not already taken.
        Copies file object to new location/name within bucket and then deletes old object.

        :param new_name: (str) new file name without extension
        :return: None
        :raises: (S3ProcessesAdapterError) if file does not exist or new name is taken
        """
        ext = f".{self.path.split('.')[-1]}"
        new_path = FilePath("/".join(self.path.split("/")[:-1]) + f"/{new_name}" + ext)
        parent_dir = FilePath("/".join(self.path.split("/")[:-1]) + "/")

        files, dirs = self.ls(path=parent_dir)
        if not self.exists():
            raise S3ProcessesAdapterError("File does not exist to rename")
        if self.check_name_taken(name=new_name, existing_names=[files for files in files.keys()] + dirs):
            raise S3ProcessesAdapterError("New file name already taken by a file or directory in this folder")

        self.copy_file(new_path=new_path)
        self.delete_file()

    def rename_folder(self, new_name: str) -> None:
        """
        Checks new name not already taken.
        Copies folder object and contents to new location/name within bucket and then deletes old object and contents.

        :param new_name: (str) new folder name
        :return: None
        :raises: (S3ProcessesAdapterError) if folder does not exist or new name is taken
        """
        new_path = FilePath("/".join(self.path.split("/")[:-1]) + f"/{new_name}")

        if self.exists(path=new_path):
            raise S3ProcessesAdapterError("New folder name already taken by a file or directory in this folder")

        self.copy_folder(new_folder=new_path)

        self.delete_folder()

    def move_file(self, destination_folder: str) -> None:
        """
        Checks new file path not already taken.
        Copies file object to new location/name within bucket and then deletes old object.

        :param destination_folder: (str) folder file is to be moved to
        :return: None
        :raises: (S3ProcessesAdapterError) if destination filepath already exists
        """
        file = self.path.split("/")[-1]
        new_path = FilePath(f"{destination_folder}/{file}")
        if self.exists(path=new_path):
            S3ProcessesAdapterError("File with same name already exists in destination folder")

        self.copy_file(new_path=new_path)
        self.delete_file()

    def move_folder(self, destination_folder: str) -> None:
        """
        Checks new folder path not already taken.
        Copies folder object and contents to new location/name within bucket and then deletes old folder.

        :param destination_folder: (str) folder to be moved to
        :return: None
        :raises: (S3ProcessesAdapterError) if destination filepath already exists
        """
        folder = self.path.split("/")[-1]
        new_path = FilePath(f"{destination_folder}/{folder}")

        if self.exists(path=new_path):
            S3ProcessesAdapterError("File/Folder with same name already exists in folder")

        self.copy_folder(new_folder=new_path)

        self.delete_folder()

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
            dest_path = FilePath(f"{destination_folder}/{path}")
            if dest_path.get_file_type(dest_path.to_string()) is not None:
                self.path = FilePath(f"{self.path}/{path}")
                self.move_file(destination_folder=destination_folder)
            else:
                self.path = FilePath(f"{self.path}/{path}")
                self.move_folder(destination_folder=destination_folder)
            self.path = origin_folder

    @staticmethod
    def check_name_taken(name: str, existing_names: List[str]) -> bool:
        """
        Checks if a name string is in a list of strings.
        :param name: (str) file or folder name
        :param existing_names: (List[str]) list of strings to check
        """
        if name in existing_names:
            return True
        else:
            return False

    def _strip_path_slash(self) -> None:
        """
        self.path has any trailing '/' stripped to account for root folder level paths e.g. s3://example-bucket/

        :return: None
        """
        self.path = FilePath(self.path.rstrip("/"))
