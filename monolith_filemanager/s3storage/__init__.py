import os
from typing import Tuple, List, Union, Any

from .bucket_manager import BucketManager
from .errors import V1EngineError
from .file_manager import FileManager
from ..path import FilePath


class V1Engine(BucketManager, FileManager):
    """
    This is the main interface for managing operations for s3 buckets and files.

    Attributes:
        resource (object): object managing the resource for s3 connection
        client (object): object managing the client for s3 connection
    """
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = super(V1Engine, cls).__new__(cls, *args, **kwargs)
        return cls._singleton

    def __init__(self) -> None:
        """
        The constructor for the V1Engine class.
        """
        try:
            import boto3
        except ImportError:
            raise V1EngineError(
                message="AWS s3 file management requires boto3 to work. Run the command: 'file-install-aws' to install "
                        "the required modules"
        )
        BucketManager.__init__(self)
        FileManager.__init__(self)
        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

    def upload_data(self, storage_path: Union[FilePath, str], data: Any) -> None:
        """
        Uploads serialised data to s3 bucket.

        :param storage_path: (str) storage path from the Notebook.get_path_for_artifact function
        :param data: (bytes) data to be upload
        :return: None
        """
        bucket, file_name, _ = V1Engine._split_s3_path(storage_path)
        self.upload_serialised_data(bucket_name=bucket, file_name=file_name, data=data)

    def upload_data_from_file(self, storage_path: str, file_path: str) -> None:
        """
        Uploads serialised data to s3 bucket.

        :param storage_path: (str) storage path in s3
        :param file_path: (str) file path of file to upload
        :return: None
        """
        bucket, file_name, _ = V1Engine._split_s3_path(storage_path)
        self.upload_file_from_disk(bucket_name=bucket, file_name=file_name, file_path=file_path)

    def create_folder(self, storage_path: str) -> str:
        """
        Creates a "folder" object in the s3 bucket when passed a filepath. Does not upload file.

        :param storage_path: (str) storage path in s3
        :return: (str) new folder name
        """
        bucket, file_name, _ = V1Engine._split_s3_path(storage_path)
        folder_name = "/".join(file_name.split("/")[:-1]) + "/"
        parent_dir = "/".join(file_name.split("/")[:-2])
        files, dirs = self.ls_folder(bucket_name=bucket, file_name=parent_dir)
        dirname = file_name
        folder = dirname.split("/")[-2]
        file_names = [x for x in files.keys()]
        if folder in file_names:
            raise V1EngineError("New folder name already taken by file in this folder")
        if self.file_exists(bucket_name=bucket, file_name=folder_name):
            folder_name = self.increment_folder_name(bucket_name=bucket, dirname=folder_name)
        self.upload_serialised_data(bucket_name=bucket, file_name=folder_name)
        return folder_name

    def increment_folder_name(self, bucket_name: str, dirname: str) -> str:
        """
        Increment folder name suffix if name prefix already exists within parent file object collection.
        :param bucket_name: (str) name of bucket containing the folder object
        :param dirname: (str) folder object name to increment
        :return: (str) new folder name
        """
        count = 2
        prefix = "/".join(dirname.split("/")[:-1])
        new_folder = prefix + f" {count}/"
        while self.file_exists(bucket_name=bucket_name, file_name=new_folder):
            count += 1
            new_folder = prefix + f" {count}/"
        self.client.put_object(Bucket=bucket_name, Key=new_folder)
        return new_folder

    def download_raw_data_file(self, storage_path: str) -> Any:
        """
        Downloads raw data from s3 bucket.

        :param storage_path: (str) storage path in the s3 storage space
        :return: (Any) file in memory (usually serialised)
        """
        bucket, file_name, short_file_name = V1Engine._split_s3_path(storage_path)
        return self.download_file_to_memory(bucket_name=bucket, file_name=file_name)

    def download_data_file(self, storage_path: Union[FilePath, str], file_path: Union[FilePath, str]) -> str:
        """
        Download data file to disk.

        :param storage_path: (Union[FilePath, str]) storage path in the s3 storage space
        :param file_path: (Union[FilePath, str]) path where file is to be saved
        :return: (str) path to where the file is downloaded to
        """
        bucket, file_name, short_file_name = V1Engine._split_s3_path(storage_path)
        output_path = os.path.join(file_path, short_file_name)
        self.download_file_to_disk(bucket_name=bucket, file_name=file_name, file_path=output_path)
        return output_path

    def delete(self, storage_path: Union[FilePath, str], folder=False) -> None:
        """
        Deletes the file from s3 or folder and file contents from s3.

        :param storage_path: (str) storage path in the s3 storage space
        :param folder: (bool)
        :return: None
        """
        bucket, file_name, short_file_name = V1Engine._split_s3_path(storage_path)
        if not folder:
            self.delete_file(bucket_name=bucket, file_name=file_name)
        else:
            self.delete_folder(bucket_name=bucket, file_name=file_name)

    def exists(self, storage_path: Union[FilePath, str]) -> bool:
        """
        Checks to see if the path exists.

        :param storage_path: (Union[FilePath, str]) path to be checked
        :return: (bool) True if path exists, False if not
        """
        bucket, file_name, short_file_name = V1Engine._split_s3_path(storage_path)
        if self.file_exists(bucket_name=bucket, file_name=file_name):
            return True
        if self.folder_exists(bucket_name=bucket, file_name=file_name):
            return True
        return False

    def ls(self, storage_path: Union[FilePath, str]) -> Tuple[dict, List[str]]:
        """
        Lists all the sub directories and sub files belonging to the self.path.

        :param storage_path: (Union[FilePath, str]) path to be inspected
        :return: (Tuple[dict, List[str]]) sub directories and sub files
        """
        bucket, file_name, short_file_name = V1Engine._split_s3_path(storage_path)
        return self.ls_folder(bucket_name=bucket, file_name=file_name)

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
