from unittest import TestCase, main
from unittest.mock import MagicMock, patch
from monolith_filemanager.s3storage.bucket_manager import BucketManager


class TestBucketManager(TestCase):

    def test_get_buckets(self):
        test = BucketManager()

        # mock some buckets using the MagicMock object
        mocked_bucket = MagicMock()
        mocked_bucket.meta.data = {"Name": "test name"}

        mocked_bucket_two = MagicMock()
        mocked_bucket_two.meta.data = {"Name": "test name two"}

        # mock the s3 resource object and get it to return the mocked buckets
        test.resource = MagicMock()
        test.resource.buckets.all.return_value = [mocked_bucket, mocked_bucket_two]

        # fire the function
        test.get_buckets()
        # mock_check.assert_called_once_with()

        # check that the name in the meta data from the mocked buckets are in the keys
        self.assertTrue(mocked_bucket_two.meta.data['Name'] in test.buckets.keys())
        self.assertTrue(mocked_bucket.meta.data['Name'] in test.buckets.keys())

        # check that there's only 2 keys corresponding with the 2 mocked buckets
        self.assertEqual(2, len(test.buckets.keys()))

        # check that passing the name into the self.buckets dict returns the right mocked objects
        self.assertEqual(mocked_bucket_two, test.buckets[mocked_bucket_two.meta.data['Name']])
        self.assertEqual(mocked_bucket, test.buckets[mocked_bucket.meta.data['Name']])

    @patch("monolith_filemanager.s3storage.bucket_manager.BucketManager._check_bucket_cache")
    def test_get_bucket(self, mock_check):
        test = BucketManager()
        test.buckets = {"test one": 1}

        self.assertEqual(test.buckets["test one"], test.get_bucket(name="test one"))
        mock_check.assert_called_once_with()
        mock_check.reset_mock()

        with self.assertRaises(Exception):
            test.get_bucket(name="test")
        mock_check.assert_called_once_with()

    def test_get_bucket_contents(self):
        test = BucketManager()

        test.client = MagicMock()
        test.client.list_objects_v2.return_value = {"Contents": [
            {"Key": "one"}, {"Key": "two"}, {"Key": "three"}, {"Key": "four"}
        ]}
        test.get_bucket = MagicMock()
        test.get_bucket_contents(bucket_name="test")
        test.get_bucket.assert_called_once_with(name="test")

        self.assertEqual(["test"], list(test.bucket_contents.keys()))
        self.assertEqual(['keys', 'contents'], list(test.bucket_contents["test"].keys()))
        self.assertEqual(['one', 'two', 'three', 'four'], list(test.bucket_contents["test"]["keys"]))
        self.assertEqual([{'Key': 'one'}, {'Key': 'two'}, {'Key': 'three'}, {'Key': 'four'}],
                         list(test.bucket_contents["test"]["contents"]))

    def test_check_bucket_cache(self):
        test = BucketManager()
        test.get_buckets = MagicMock()

        test.buckets = [1]
        test._check_bucket_cache()

        test.buckets = []
        test._check_bucket_cache()

        test.get_buckets.assert_called_once_with()

    def test_create_bucket(self):
        test = BucketManager()
        test.resource = MagicMock()
        test.get_buckets = MagicMock()
        test._check_bucket_cache = MagicMock()

        test.create_bucket(name="test")

        test._check_bucket_cache.assert_called_once_with()
        test.resource.create_bucket.assert_called_once_with(Bucket="test")
        test.get_buckets.assert_called_once_with()

        test.buckets = {"test": 1}

        with self.assertRaises(Exception):
            test.create_bucket(name="test")

    def test_delete_bucket(self):
        test = BucketManager()
        test.resource = MagicMock()
        test.buckets = {"test": 1}
        test._check_bucket_cache = MagicMock()

        test.delete_bucket(name="test")

        test._check_bucket_cache.assert_called_once_with()
        test.resource.delete_bucket.assert_called_once_with(Bucket="test",
                                                            DeleteIfNonEmpty=False)
        self.assertEqual({}, test.buckets)

        with self.assertRaises(Exception):
            test.delete_bucket(name="test")


if __name__ == "__main__":
    main()
