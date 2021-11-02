from unittest import TestCase, main
from mock import patch, MagicMock
from monolith_filemanager.s3storage import V1Engine, V1EngineError


class TestV1Engine(TestCase):

    @patch("boto3.resource")
    @patch("boto3.client")
    @patch("monolith_filemanager.s3storage.FileManager.__init__")
    @patch("monolith_filemanager.s3storage.BucketManager.__init__")
    def setUp(self, bucket_init_mock, file_init_mock, mock_client, mock_resource) -> None:
        self.test = V1Engine()

    @patch("boto3.resource")
    @patch("boto3.client")
    @patch("monolith_filemanager.s3storage.FileManager.__init__")
    @patch("monolith_filemanager.s3storage.BucketManager.__init__")
    def test___init__(self, bucket_init_mock, file_init_mock, mock_client, mock_resource):
        # fire the __init__
        test = V1Engine()

        # check that the __init__ methods of the super classes are being called once without the engine self
        bucket_init_mock.assert_called_once_with(test)
        file_init_mock.assert_called_once_with(test)

        # check that the client and resource __init__ s are fired once with the 's3' argument
        mock_client.assert_called_once_with("s3")
        mock_resource.assert_called_once_with("s3")

        test_two = V1Engine()

        # test the singleton implementation
        self.assertEqual(id(test), id(test_two))

    @patch("monolith_filemanager.s3storage.FileManager.upload_serialised_data")
    def test_upload_data(self, mock_upload):
        self.test.upload_data(storage_path="s3://one/two/three", data="test")
        mock_upload.assert_called_once_with(bucket_name='one', data='test', file_name='two/three')

    @patch("monolith_filemanager.s3storage.FileManager.upload_file_from_disk")
    def test_upload_data_from_file(self, mock_upload):
        mock_file_path = MagicMock()
        self.test.upload_data_from_file(storage_path="s3://one/two/three", file_path=mock_file_path)
        mock_upload.assert_called_once_with(bucket_name='one', file_name='two/three', file_path=mock_file_path)

    @patch("monolith_filemanager.s3storage.V1Engine.increment_folder_name")
    @patch("monolith_filemanager.s3storage.FileManager.file_exists")
    @patch("monolith_filemanager.s3storage.V1Engine.ls_folder")
    @patch("monolith_filemanager.s3storage.FileManager.upload_serialised_data")
    def test_create_folder(self, mock_upload, mock_ls_folder, mock_file_exits, mock_increment_folder_name):
        # test with name clash
        mock_ls_folder.return_value = ({"file1.txt": {}, "three": {}}, ["dir1", "dir2"])
        mock_file_path = "s3://one/two/three/four"
        with self.assertRaises(V1EngineError):
            self.test.create_folder(storage_path=mock_file_path)

        # test with no name clash and no incrementing
        mock_file_exits.return_value = False
        mock_ls_folder.return_value = ({"file1.txt": {}, "file2.txt": {}}, ["dir1", "dir2"])
        mock_file_path = "s3://one/two/three/four"
        self.test.create_folder(storage_path=mock_file_path)
        mock_upload.assert_called_once_with(bucket_name="one", file_name="two/three/")
        mock_increment_folder_name.assert_has_calls = []

        # test with no name clash and with incrementing
        mock_file_exits.reset_mock()
        mock_upload.reset_mock()
        mock_increment_folder_name.return_value = "two/three 2/"
        mock_file_exits.return_value = True
        mock_ls_folder.return_value = ({"file1.txt": {}, "file2.txt": {}}, ["dir1", "dir2"])
        mock_file_path = "s3://one/two/three/four"
        self.test.create_folder(storage_path=mock_file_path)
        mock_upload.assert_called_once_with(bucket_name="one", file_name="two/three 2/")
        mock_increment_folder_name.assert_called_once_with(bucket_name="one", dirname="two/three/")

    @patch("monolith_filemanager.s3storage.file_manager.FileManager.file_exists")
    def test_increment_folder_name(self, mock_file_exists):
        mock_bucket = "mock-bucket"
        mock_dirname = "mock/folder/file"
        mock_file_exists.return_value = False

        self.test.increment_folder_name(bucket_name=mock_bucket, dirname=mock_dirname)
        self.test.client.put_object.assert_called_once_with(Bucket=mock_bucket, Key="mock/folder 2/")

        self.test.client.reset_mock()
        mock_file_exists.side_effect = [True, False]
        self.test.increment_folder_name(bucket_name=mock_bucket, dirname=mock_dirname)
        self.test.client.put_object.assert_called_once_with(Bucket=mock_bucket, Key="mock/folder 3/")

    @patch("monolith_filemanager.s3storage.FileManager.download_file_to_memory")
    def test_download_raw_data_file(self, mock_download):
        self.test.download_raw_data_file(storage_path="s3://one/two/three")
        mock_download.assert_called_once_with(bucket_name='one', file_name='two/three')

    @patch("monolith_filemanager.s3storage.FileManager.download_file_to_disk")
    def test_download_data_file(self, mock_download_file_to_disk):
        self.test.download_data_file(storage_path="s3://one/two/three", file_path="test path")
        mock_download_file_to_disk.assert_called_once_with(bucket_name="one",
                                                           file_name="two/three",
                                                           file_path='test path/three')

    @patch("monolith_filemanager.s3storage.FileManager.delete_file")
    def test_delete(self, mock_delete_file):
        self.test.delete(storage_path="s3://this/is/a/path.txt")
        mock_delete_file.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')

    @patch("monolith_filemanager.s3storage.FileManager.file_exists")
    @patch("monolith_filemanager.s3storage.FileManager.folder_exists")
    def test_file_exists(self, mock_folder_exists, mock_file_exists):
        mock_file_exists.return_value = True
        mock_folder_exists.return_value = False
        exists = self.test.exists(storage_path="s3://this/is/a/path.txt")
        mock_file_exists.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')
        self.assertTrue(exists)

    @patch("monolith_filemanager.s3storage.FileManager.file_exists")
    @patch("monolith_filemanager.s3storage.FileManager.folder_exists")
    def test_folder_exists(self, mock_folder_exists, mock_file_exists):
        mock_file_exists.return_value = False
        mock_folder_exists.return_value = True
        exists = self.test.exists(storage_path="s3://this/is/a/path.txt")
        mock_file_exists.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')
        mock_folder_exists.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')
        self.assertTrue(exists)

    @patch("monolith_filemanager.s3storage.FileManager.file_exists")
    @patch("monolith_filemanager.s3storage.FileManager.folder_exists")
    def test_neither_file_or_folder_exists(self, mock_folder_exists, mock_file_exists):
        mock_file_exists.return_value = False
        mock_folder_exists.return_value = False
        exists = self.test.exists(storage_path="s3://this/is/a/path.txt")
        mock_file_exists.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')
        mock_folder_exists.assert_called_once_with(bucket_name='this', file_name='is/a/path.txt')
        self.assertFalse(exists)

    @patch("monolith_filemanager.s3storage.FileManager.ls_folder")
    def test_ls(self, mock_ls):
        self.test.ls(storage_path="s3://this/is/a/folder")
        mock_ls.assert_called_once_with(bucket_name='this', file_name='is/a/folder')


if __name__ == "__main__":
    main()
