from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call
from monolith_filemanager.adapters.s3_processes import S3ProcessesAdapter, S3ProcessesAdapterError


class TestS3ProcessesAdapter(TestCase):

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def setUp(self, mock_init) -> None:
        mock_init.return_value = None
        self.test_file = S3ProcessesAdapter(file_path="mock/folder/test.xlsx")
        self.test_file.path = "mock/folder/test.xlsx"
        self.test_folder = S3ProcessesAdapter(file_path="mock/folder/path")
        self.test_folder.path = "mock/folder/path"

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter._strip_path_slash")
    @patch("monolith_filemanager.adapters.s3_processes.V1Engine")
    @patch("monolith_filemanager.adapters.s3_processes.Base.__init__")
    def test___init__(self, mock_init, mock_engine, mock_strip_path_slash):
        mock_init.return_value = None
        mock_strip_path_slash.return_value = None
        test = S3ProcessesAdapter(file_path="test")

        mock_init.assert_called_once_with(file_path="test")
        mock_engine.assert_called_once_with()
        self.assertEqual(mock_engine.return_value, test._engine)
        mock_strip_path_slash.assert_called_once_with()

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_local_file_object(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test path")
        test.file_types = MagicMock()
        test.path = MagicMock()
        out_come = test.local_file_object()

        test.file_types.get_file.assert_called_once_with(file_path=test.path)
        test.file_types.get_file.return_value.assert_called_once_with(path=test.path)
        self.assertEqual(test.file_types.get_file.return_value.return_value, out_come)

    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.local_file_object")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_read_file(self, mock_init, mock_local_file_object, mock_file_path):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test.path = MagicMock()
        test._cache = MagicMock()
        test._pickle_factory = MagicMock()
        test._engine = MagicMock()
        test.file_types = MagicMock()
        test.path.file_type = "pickle"

        with self.assertRaises(S3ProcessesAdapterError):
            test.read_file()

        test.path.file_type = "not pickle"
        second_cached_path = test.path.to_string.return_value
        second_out_come = test.read_file()

        test._cache.create_cache.assert_called_once_with()
        test._engine.download_data_file.assert_called_once_with(storage_path=second_cached_path,
                                                                file_path=test._cache.cache_path)
        mock_local_file_object.return_value.read.assert_called_once_with()
        mock_file_path.assert_called_once_with(test._engine.download_data_file.return_value)
        self.assertEqual(mock_file_path.return_value, test.path)
        self.assertEqual(mock_local_file_object.return_value.read.return_value, second_out_come)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_read_raw_file(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test.path = MagicMock()
        test._engine = MagicMock()

        out_come = test.read_raw_file()
        test._engine.download_raw_data_file.assert_called_once_with(storage_path=test.path.to_string.return_value)
        self.assertEqual(out_come, test._engine.download_raw_data_file.return_value)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_custom_read_file(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test path")
        test.path = MagicMock()
        test._cache = MagicMock()
        test._engine = MagicMock()
        test.file_types = MagicMock()
        test.path.file_type = "any"
        source_path = test.path
        custom_read_function = MagicMock(name='read function')
        data_output = MagicMock(name='data')
        custom_read_function.return_value = data_output

        out_come = test.custom_read_file(custom_read_function)

        test._cache.create_cache.assert_called_once_with()
        test._engine.download_data_file.assert_called_once_with(storage_path=source_path,
                                                                file_path=test._cache.cache_path)

        self.assertEqual(test._engine.download_data_file.return_value, test.path)
        custom_read_function.assert_called_once_with(test.path)
        self.assertEqual(out_come, data_output)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.local_file_object")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_write_file_supports_s3(self, mock_init, mock_local_file_object):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test._engine = MagicMock()
        test.path = MagicMock()
        mock_local_file_object.return_value.supports_s3.return_value = True
        mock_data = MagicMock()
        test.write_file(data=mock_data)
        mock_local_file_object.return_value.write.assert_called_once_with(mock_data)

    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.local_file_object")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_write_file_not_supports_s3(self, mock_init, mock_local_file_object, mock_file_path):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test._engine = MagicMock()
        test.path = MagicMock()
        test._cache = MagicMock()
        mock_local_file_object.return_value.supports_s3.return_value = False
        mock_local_file_object.return_value.path = test.path
        mock_data = MagicMock()
        test.write_file(data=mock_data)
        test._engine.upload_data_from_file.assert_called_once_with(file_path=mock_file_path.return_value.to_string.return_value, storage_path=test.path.to_string.return_value)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_write_raw_file(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test._engine = MagicMock()
        test.path = MagicMock()

        mock_data = MagicMock()
        test.write_raw_file(data=mock_data)
        test._engine.upload_data.assert_called_once_with(storage_path=test.path.to_string.return_value, data=mock_data)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_delete_file(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test path")
        test._engine = MagicMock()
        test.path = MagicMock()
        test.delete_file()

        test._engine.delete.assert_called_once_with(storage_path=test.path)

    @patch("monolith_filemanager.adapters.s3_processes.V1Engine._split_s3_path")
    def test_delete_folder(self, mock_split_path):
        mock_engine = MagicMock()
        mock_engine.delete_file.return_value = None
        self.test_folder._engine = mock_engine
        mock_split_path.return_value = ("mock-bucket", "mock/folder", "folder")

        self.test_folder.delete_folder()
        mock_engine.delete_file.assert_called_once_with(bucket_name="mock-bucket", file_name="mock/folder/")

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.increment_files")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.check_name_taken")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.ls")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_write_stream(self, mock_init, mock_ls, mock_name_taken, mock_exists, mock_increment_files):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test._engine = MagicMock()
        test.path = "mock/folder/file.txt"
        test._cache = MagicMock()
        mock_ls.return_value = ([], [])
        mock_stream = MagicMock()
        # test name already taken
        mock_name_taken.return_value = True
        with self.assertRaises(S3ProcessesAdapterError):
            test.write_stream(mock_stream)
        mock_stream.save.assert_called_once()

        # test already exists
        mock_stream.reset_mock()

        mock_name_taken.return_value = False
        mock_exists.return_value = True
        mock_increment_files.return_value = None
        self.assertEqual("file.txt", test.write_stream(mock_stream))
        cache_path = mock_stream.save.call_args_list[0][0][0]
        test._engine.upload_data_from_file.assert_called_once_with(storage_path=test.path, file_path=cache_path)
        mock_increment_files.assert_called_once_with()
        mock_stream.save.assert_called_once()

        # test doesn't already exist
        mock_stream.reset_mock()
        test._engine.reset_mock()
        mock_increment_files.reset_mock()
        mock_exists.return_value = False
        self.assertEqual("file.txt", test.write_stream(mock_stream))
        mock_stream.save.assert_called_once()
        cache_path = mock_stream.save.call_args_list[0][0][0]
        test._engine.upload_data_from_file.assert_called_once_with(storage_path=test.path, file_path=cache_path)
        mock_increment_files.assert_has_calls = []

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_increment_files(self, mock_init, mock_exists):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path=MagicMock())
        test.path = "mock/path/folder/file.txt"
        mock_exists.return_value = False
        test.increment_files()
        self.assertEqual("mock/path/folder/file 2.txt", test.path)

        test.path = "mock/path/folder/file.txt"
        mock_exists.side_effect = [True, False]
        test.increment_files()
        self.assertEqual("mock/path/folder/file 3.txt", test.path)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_create_directory_if_not_exists(self, mock_init):
        mock_init.return_value = None
        mock_path = MagicMock()
        test = S3ProcessesAdapter(file_path=mock_path)
        test._engine = MagicMock()
        test.path = mock_path

        test.create_directory_if_not_exists()
        test._engine.create_folder.assert_called_once_with(storage_path=mock_path)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_exists(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test path")
        test._engine = MagicMock()
        test.path = MagicMock()

        test.exists()
        test._engine.exists.assert_called_once_with(storage_path=test.path)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_ls(self, mock_init):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test path")
        test._engine = MagicMock()
        test.path = MagicMock()

        test.ls()
        test._engine.ls.assert_called_once_with(storage_path=test.path.to_string.return_value)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.delete_file")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test_batch_delete(self, mock_init, mock_delete_file):
        mock_init.return_value = None
        test = S3ProcessesAdapter(file_path="test/path")
        test.path = "test/path"
        test.path = "mock/folder/path"
        mock_paths = ["mock_folder", "mock_file"]
        mock_delete_file.side_effect = [None, None]
        test.batch_delete(paths=mock_paths)
        mock_delete_file.assert_has_calls = [call(path=test.path + mock_paths[0]),
                                             call(path=test.path + mock_paths[1])]

    def test_copy_file(self):
        mock_new_path = "mock/new/path"
        mock_engine = MagicMock()
        mock_engine._split_s3_path.side_effect = [("mock-bucket", "old/file.txt", None),
                                                  ("mock-bucket", "new/file.txt", None)]
        mockObject = MagicMock()
        mockObject.copy_from.return_value = None
        mock_engine.resource.Object.return_value = mockObject

        self.test_file._engine = mock_engine
        self.test_file.copy_file(mock_new_path)
        mock_engine._split_s3_path.assert_has_calls = [call(self.test_file.path), call(mock_new_path)]
        mockObject.copy_from.assert_called_once_with(CopySource="mock-bucket/old/file.txt")

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.delete_file")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.copy_file")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.check_name_taken")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.ls")
    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    def test_rename_file(self, mock_filepath, mock_ls, mock_exists, mock_check_name_taken, mock_copy_file,
                         mock_delete_file):
        new_name = "new_name"
        mock_ext = ".xlsx"
        mock_filepath.side_effect = ["/".join(self.test_file.path.split("/")[:-1]) + f"/{new_name}" + mock_ext,
                                      "/".join(self.test_file.path.split("/")[:-1]) + "/"]
        mock_ls.return_value = ({}, [])
        mock_exists.return_value = True
        mock_check_name_taken.return_value = False

        mock_copy_file.return_value = None
        mock_delete_file.return_value = None

        self.test_file.rename_file(new_name=new_name)
        mock_ls.assert_called_once_with(path="mock/folder/")
        mock_copy_file.assert_called_once_with(new_path='mock/folder/new_name.xlsx')
        mock_delete_file.assert_called_once_with()

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.delete_folder")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.copy_folder")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    def test_rename_folder(self, mock_filepath, mock_exists, mock_copy_folder, mock_delete_folder):
        new_name = "new_folder"
        mock_filepath.return_value = "/".join(self.test_folder.path.split("/")[:-1]) + f"/{new_name}"
        mock_exists.return_value = False
        mock_copy_folder.return_value = None
        mock_delete_folder.return_value = None
        self.test_folder.rename_folder(new_name=new_name)

        mock_copy_folder.assert_called_once_with(new_folder=f"mock/folder/{new_name}")
        mock_delete_folder.assert_called_once_with()

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.delete_file")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.copy_file")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    def test_move_file(self, mock_filepath, mock_exists, mock_copy_file, mock_delete_file):
        mock_destination_folder = "mock/new/path"
        mock_filepath.return_value = "mock/new/path/file.txt"
        mock_exists.return_value = False

        self.test_file.move_file(destination_folder=mock_destination_folder)
        mock_copy_file.assert_called_once_with(new_path=mock_filepath.return_value)
        mock_delete_file.assert_called_once_with()

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.delete_folder")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.copy_folder")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    def test_move_folder(self, mock_filepath, mock_exists, mock_copy_folder, mock_delete_folder):
        mock_destination_folder = "mock/new/path"
        mock_filepath.return_value = "mock/new/path/folder"
        mock_exists.return_value = False

        self.test_folder.move_folder(destination_folder=mock_destination_folder)
        mock_copy_folder.assert_called_once_with(new_folder=mock_filepath.return_value)
        mock_delete_folder.assert_called_once_with()

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.move_folder")
    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.move_file")
    @patch("monolith_filemanager.adapters.s3_processes.FilePath")
    def test_batch_move(self, mock_filepath, mock_move_file, mock_move_folder):
        mock_paths = ["test.xlsx", "test_folder"]
        mock_destination_folder = "mock/destination/folder"
        mock_filepath1 = MagicMock()
        mock_filepath1.to_string.return_value = f"{mock_destination_folder}/{mock_paths[0]}"
        mock_filepath1.get_file_type.return_value = "xlsx"
        mock_filepath2 = MagicMock()
        mock_filepath2.to_string.return_value = f"{mock_destination_folder}/{mock_paths[1]}"
        mock_filepath2.get_file_type.return_value = None
        mock_filepath.side_effect = [mock_filepath1, None, mock_filepath2, None]

        mock_move_file.return_value = None
        mock_move_folder.return_value = None

        self.test_folder.batch_move(paths=mock_paths, destination_folder=mock_destination_folder)
        mock_filepath.assert_has_calls([call(f"{mock_destination_folder}/{mock_paths[0]}"),
                                        call(f"{self.test_folder.path}/{mock_paths[0]}"),
                                        call(f"{mock_destination_folder}/{mock_paths[1]}"),
                                        call(f"{self.test_folder.path}/{mock_paths[1]}")])
        mock_move_file.assert_called_once_with(destination_folder=mock_destination_folder)
        mock_move_folder.assert_called_once_with(destination_folder=mock_destination_folder)

    @patch("monolith_filemanager.adapters.s3_processes.S3ProcessesAdapter.__init__")
    def test__strip_path_slash(self, mock_init):
        mock_init.return_value = None
        mock_path = "mock/folder/path/"
        test_folder = S3ProcessesAdapter(file_path=mock_path)
        test_folder.path = mock_path
        test_folder._strip_path_slash()
        self.assertEqual(mock_path.rstrip("/"), test_folder.path)


if __name__ == "__main__":
    main()
