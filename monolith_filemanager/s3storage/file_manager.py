from botocore.exceptions import ClientError
import os
from typing import Any, Tuple, List, Optional
from urllib.parse import unquote

from .errors import FileManagerError


class FileManager:
    """
    This is a class managing the operations for s3 files.

    Attributes:
        resource (object): object managing the resource for s3 connection (None unless overridden by subclass like V1Engine)
        client (object): object managing the client for s3 connection (None unless overridden by subclass like V1Engine)
    """

    BASE_DIR = os.getcwd()
    FILE_PATH = "/tests/monolith_filemanager.connection_type.s3storage/"

    def __init__(self):
        """
        The constructor for the BucketManager class.
        """
        self.resource = None
        self.client = None

    @staticmethod
    def _prep_remote_name(name: str) -> str:
        """
        Prepares the file name in remote format.

        :param name: (str) name of the file
        :return: (str) name formatted for remote conventions
        """
        if " " in name:
            raise FileManagerError(message="space detected in the file name {}".format(name))
        components = name.replace("./", "").split(".")
        if len(components) != 2:
            raise FileManagerError(message="one and only one full stop should be in the name")
        return components[0] + "-remote." + components[1]

    def upload_file_from_disk(self, bucket_name: str, file_name: str, file_path: str) -> None:
        """
        Uploads file from disk to s3 storage.

        :param bucket_name: (str) name of bucket for file to be stored in
        :param file_name: (str) file name to save file as in s3
        :param file_path: (str) path to file being uploaded
        :return:
        """
        self.client.upload_file(file_path,
                                bucket_name,
                                file_name)

    def upload_serialised_data(self, bucket_name: str, file_name: str, data: Optional[bytes] = None) -> None:
        """
        Uploads serialised data to bucket.

        :param bucket_name: (str) name of bucket for data to be stored in
        :param file_name: (str) name for which the data is stored under
        :param data: (Optional[bytes]) data to be stored in s3
        :return: None
        """
        if data:
            self.client.put_object(Body=data, Bucket=bucket_name, Key=file_name)
        else:
            self.client.put_object(Bucket=bucket_name, Key=file_name)

    def download_file_to_disk(self, bucket_name: str, file_name: str, file_path: str) -> None:
        """
        Downloads file from bucket to disk (alter self.BASE_DIR and self.FILE_PATH to alter download destination).

        :param bucket_name: (str) name of bucket for file to be downloaded from
        :param file_name: (str) name of file being downloaded
        :param file_path: (str) path of where file is stored
        :return: None
        """
        self.client.download_file(bucket_name,
                                  file_name,
                                  file_path)

    def download_file_to_memory(self, bucket_name: str, file_name: str) -> Any:
        """
        Downloads file to memory.

        :param bucket_name: (str) name of bucket for file to be downloaded from
        :param file_name: (str) name of file being downloaded
        :return: (Any) downloaded file
        """
        outcome = self.client.get_object(Bucket=bucket_name, Key=file_name)
        return outcome["Body"].read()

    def delete_file(self, bucket_name: str, file_name: str) -> None:
        """
        Deletes file from bucket.

        :param bucket_name: (str) name of bucket for file
        :param file_name: (str) name of file being deleted
        :return: None
        """
        bucket = self.resource.Bucket(bucket_name)
        bucket.objects.filter(Prefix=file_name).delete()

    def delete_folder(self, bucket_name: str, file_name: str) -> None:
        """
        Deletes file from bucket.

        :param bucket_name: (str) name of bucket for file
        :param file_name: (str) name of file being deleted
        :return: None
        """
        self.delete_file(bucket_name=bucket_name, file_name=f"{file_name}/")

    def file_exists(self, bucket_name, file_name) -> bool:
        """
        Check if file exists in a bucket.

        :param bucket_name: (str) name of bucket for file
        :param file_name: (str) name of file to search for
        :return: None
        """
        try:
            self.client.head_object(Bucket=bucket_name, Key=file_name)
            return True
        except ClientError:
            return False
        
    def folder_exists(self, bucket_name, file_name) -> bool:
        try:
            if 'Contents' in self.client.list_objects(Bucket=bucket_name, Prefix=file_name, MaxKeys=1):
                return True
            return False
        except ClientError:
            return False

    def ls_folder(self, bucket_name: str, file_name: str) -> Tuple[dict, List[str]]:
        """
        Lists all the sub directories and sub files belonging to the self.path.

        :param bucket_name: (str) the name of the bucket
        :param file_name: (str) the name of the file
        :return: (Tuple[List[str], List[str]]) sub files with metadata and sub directories
        """
        paginator = self.client.get_paginator('list_objects')
        prefix = file_name
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
        dirs = []
        files = {}

        for result in pages:
            dirs += [unquote(x.get('Prefix').split("/")[-2]) for x in result.get('CommonPrefixes', []) if x is not None]
            if result.get("Contents"):
                for x in result.get("Contents"):
                    last_modified, size = self.get_file_info(x)
                    files[unquote(x.get('Key').split("/")[-1])] = {"last_modified": last_modified, "size": size}
        return files, dirs

    @staticmethod
    def get_file_info(s3_object: dict) -> Tuple[str, int]:
        """
        Returns last modified date and file size in bytes.

        :param s3_object: (dict) the s3 file object
        :return: (Tuple[str, int]) last_modified datetime and file size in bytes
        """
        last_mod = s3_object.get('LastModified').strftime("%Y-%m-%d %H:%M:%S")
        size = s3_object.get('Size')
        return last_mod, size
