import datetime
from unittest import TestCase, main
from unittest.mock import MagicMock, patch
from monolith_filemanager.s3storage.file_manager import FileManager


class TestFileManager(TestCase):

    def test__prep_remote_name(self):
        out_come = FileManager._prep_remote_name(name="test.txt")
        self.assertEqual("test-remote.txt", out_come)

        with self.assertRaises(Exception):
            FileManager._prep_remote_name(name="test.txt.py")

        with self.assertRaises(Exception):
            FileManager._prep_remote_name(name="test")

    def test_upload_file_from_disk(self):
        test = FileManager()
        test.client = MagicMock()

        test.upload_file_from_disk(bucket_name="test-bucket", file_name="foo/bar/saved-file", file_path="local/test-file")

        test.client.upload_file.assert_called_once_with("local/test-file", "test-bucket", "foo/bar/saved-file")

    def test_upload_serialised_data(self):
        test = FileManager()
        test.client = MagicMock()

        test.upload_serialised_data(bucket_name="test-bucket", file_name="test-file",
                                    data=[1, 2, 3])

        test.client.put_object.assert_called_once_with(Body=[1, 2, 3],
                                                       Bucket="test-bucket",
                                                       Key="test-file")

        test.client.reset_mock()

        test.upload_serialised_data(bucket_name="test-bucket", file_name="test-file",
                                    data=None)

        test.client.put_object.assert_called_once_with(Bucket="test-bucket", Key="test-file")

    def test_download_file_to_disk(self):
        test = FileManager()
        test.client = MagicMock()

        test.download_file_to_disk(bucket_name="test-bucket", file_name="test.txt", file_path="test path")
        test.client.download_file.assert_called_once_with("test-bucket",
                                                          "test.txt",
                                                          "test path")

    def test_download_file_to_memory(self):
        test = FileManager()
        test.client = MagicMock()
        test.client.get_object.return_value.__getitem__.return_value.read.return_value = "test"

        out_come = test.download_file_to_memory(bucket_name="test-bucket", file_name="test.txt")

        test.client.get_object.assert_called_once_with(Bucket='test-bucket', Key='test.txt')
        self.assertEqual("test", out_come)

    def test_delete_file(self):
        test = FileManager()
        test.client = MagicMock()
        mock_resource = MagicMock()
        mock_bucket = MagicMock()
        mock_objects = MagicMock()
        mock_bucket.objects.filter.return_value = mock_objects
        mock_resource.Bucket.return_value = mock_bucket

        test.resource = mock_resource
        test.delete_file(bucket_name="test-bucket", file_name="test.txt")

        test.resource.Bucket.assert_called_once_with("test-bucket")
        mock_bucket.objects.filter.assert_called_once_with(Prefix="test.txt")
        mock_objects.delete.assert_called_once_with()

    def test_file_exists(self):
        test = FileManager()
        test.client = MagicMock()

        test.file_exists(bucket_name="test-bucket", file_name="test.txt")

        test.client.head_object.assert_called_once_with(Bucket="test-bucket", Key="test.txt")

    def test_folder_exists(self):
        test = FileManager()
        test.client = MagicMock()

        test.folder_exists(bucket_name="test-bucket", file_name="test.txt")

        test.client.list_objects.assert_called_once_with(Bucket="test-bucket", Prefix="test.txt", MaxKeys=1)

    def test_ls_folder(self):
        test = FileManager()
        test.client = MagicMock()
        paginator = test.client.get_paginator.return_value
        timestamp = datetime.datetime.utcnow()
        pages = [
            {
                'CommonPrefixes': [
                    {'Prefix': 'some/folder/foo/'},
                    {'Prefix': 'some/folder/bar/'},
                ],
                'Contents': [
                    {'Key': 'some/folder/alpha', "LastModified": timestamp, "Size": 100},
                    {'Key': 'some/folder/beta', "LastModified": timestamp, "Size": 100},
                ],
            },
            {
                'CommonPrefixes': [
                    {'Prefix': 'some/folder/baz/'},
                ],
            },
            {
                'Contents': [
                    {'Key': 'some/folder/gamma', "LastModified": timestamp, "Size": 100},
                    {'Key': 'some/folder/delta', "LastModified": timestamp, "Size": 100},
                    {'Key': 'some/folder/theta', "LastModified": timestamp, "Size": 100},
                ],
            },
        ]
        paginator.paginate.return_value = pages

        out_come = test.ls_folder(bucket_name="test-bucket", file_name="some/folder")

        test.client.get_paginator.assert_called_once_with('list_objects')
        paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="some/folder/", Delimiter='/')

        expected_out_come = (
            {x: {"last_modified": timestamp.strftime("%Y-%m-%d %H:%M:%S"), "size": 100} for x in
             ['alpha', 'beta', 'gamma', 'delta', 'theta']},
            ['foo', 'bar', 'baz']
        )
        self.assertEqual(expected_out_come, out_come)


if __name__ == "__main__":
    main()
