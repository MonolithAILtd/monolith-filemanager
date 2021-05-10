from typing import Optional, Dict, Any

from .errors import BucketManagetError


class BucketManager:
    """
    This is a class managing the operations for s3 buckets.

    Attributes:
        resource (Any): object managing the resource for s3 connection (None unless overridden by subclass like V1Engine)
        client (Any): object managing the client for s3 connection (None unless overridden by subclass like V1Engine)
        buckets (dict): keeps reference of buckets. Keys are made of bucket names
        bucket_contents (dict) keeps reference of bucket contents. Keys are made of bucket names
    """
    def __init__(self):
        """
        The constructor for the BucketManager class.
        """
        self.resource: Optional[Any] = None
        self.client: Optional[Any] = None
        self.buckets: Dict = dict()
        self.bucket_contents: Dict = dict()

    def get_buckets(self) -> None:
        """
        Fills self.buckets with all the buckets from S3.

        :return: None
        """
        self.buckets = dict()
        for bucket in self.resource.buckets.all():
            self.buckets[str(bucket.meta.data["Name"])] = bucket

    def get_bucket(self, name: str):
        """
        Gets bucket object from self.buckets.

        :param name: (str) name of bucket required
        :return: bucket object
        """
        self._check_bucket_cache()
        bucket = self.buckets.get(name)
        if not bucket:
            raise BucketManagetError(message="bucket {} not available. please pick from: {}".format(name,
                                                                                                    self.buckets.keys()
                                                                                                    ))
        return bucket

    def get_bucket_contents(self, bucket_name: str) -> None:
        """
        Gets a list of files from a bucket and stores it in self.bucket_contents with the key of the bucket name.
        
        :param bucket_name: (str) name of the bucket required
        :return: None
        """
        self.get_bucket(name=bucket_name)
        package = dict()
        contents = self.client.list_objects_v2(Bucket=bucket_name)["Contents"]
        package["keys"] = [i["Key"] for i in contents]
        package["contents"] = contents
        self.bucket_contents[bucket_name] = package

    def _check_bucket_cache(self) -> None:
        """
        Fills self.buckets if self.buckets is empty (private).
        
        :return: None
        """
        if len(self.buckets) == 0:
            self.get_buckets()

    def create_bucket(self, name: str) -> None:
        """
        Creates a bucket in S3 storage.
        
        :param name: (str) name of bucket you want to create.
        :return: None
        """
        self._check_bucket_cache()
        if self.buckets.get(name):
            raise BucketManagetError(message="{} already exists".format(name))
        # TODO look into defining the region for the create_bucket function
        self.resource.create_bucket(Bucket=name)
        self.get_buckets()

    def delete_bucket(self, name: str, force: Optional[bool] = False) -> None:
        """
        Deletes bucket (does not support buckets that have contents).
        
        :param name: (str) name of bucket you want to delete
        :param force: (bool) if True, will delete even if bucket has contents
        :return: None
        """
        self._check_bucket_cache()
        if not self.buckets.get(name):
            raise BucketManagetError(message="{} does not exist".format(name))
        self.resource.delete_bucket(Bucket=name, DeleteIfNonEmpty=force)
        del self.buckets[name]
