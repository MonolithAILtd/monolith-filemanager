from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call

from monolith_filemanager.adapters.local_file_processes import LocalFileProcessesAdapter, LocalProcessesAdapterError


class TestLocalFileProcessesAdapterWithoutInit(TestCase):

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def setUp(self, mock_init) -> None:
        # todo - flesh this out later to apply to more test cases
        mock_init.return_value = None
        self.test_folder = LocalFileProcessesAdapter(file_path="mock/folder/path", caching=MagicMock())
        self.test_folder.path = "mock/folder/path"
        self.test_file = LocalFileProcessesAdapter(file_path="mock/folder/test.xlsx", caching=MagicMock())
        self.test_file.path = "mock/folder/test.xlsx"

    @patch("monolith_filemanager.adapters.local_file_processes.os.environ", {"PYTHONPATH": "mock/python/path"})
    def test___init__local(self):
        mock_path = "mock/folder/path"
        obj = LocalFileProcessesAdapter(file_path=mock_path)
        self.assertIsInstance(obj, LocalFileProcessesAdapter)
        self.assertEqual(obj.path, mock_path)
        self.assertEqual(obj._s3, False)
        self.assertEqual(obj.python_path, "mock/python/path")

    @patch("monolith_filemanager.adapters.local_file_processes.os.environ", {})
    def test___init__local_missing_pythonpath(self):
        mock_path = "mock/folder/path"
        obj = LocalFileProcessesAdapter(file_path=mock_path)
        self.assertIsInstance(obj, LocalFileProcessesAdapter)
        self.assertEqual(obj.path, mock_path)
        self.assertEqual(obj._s3, False)
        self.assertEqual(obj.python_path, "")

    def test_check_local_file(self):
        mock_path = MagicMock()

        mock_path.root_exists = True
        mock_path.file_exists = True
        LocalFileProcessesAdapter.check_local_file(path=mock_path)

        mock_path.root_exists = False
        mock_path.file_exists = True
        with self.assertRaises(Exception):
            LocalFileProcessesAdapter.check_local_file(path=mock_path)

        mock_path.root_exists = True
        mock_path.file_exists = False
        with self.assertRaises(Exception):
            LocalFileProcessesAdapter.check_local_file(path=mock_path)

        mock_path.root_exists = False
        mock_path.file_exists = False
        with self.assertRaises(Exception):
            LocalFileProcessesAdapter.check_local_file(path=mock_path)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_local_file_object(self, mock_init):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.file_types = MagicMock()
        test.path = MagicMock()
        out_come = test.local_file_object()

        test.file_types.get_file.assert_called_once_with(file_path=test.path)
        test.file_types.get_file.return_value.assert_called_once_with(path=test.path)
        self.assertEqual(test.file_types.get_file.return_value.return_value, out_come)

    @patch("flask.send_from_directory")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_export_file(self, mock_init, mock_check_local_file, mock_send_from_directory):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        test.path.root = "test.csv"
        test.python_path = "python/path"

        out_come = test.export_file()

        mock_check_local_file.assert_called_once_with(path=test.path)
        mock_send_from_directory.assert_called_once_with(directory="python/path/test.csv", filename=test.path.file)
        self.assertEqual(out_come, mock_send_from_directory.return_value)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.local_file_object")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_read_file(self, mock_init, mock_check, mock_local_file_object):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        test.path.file_type = "not pickle"

        out_come = test.read_file()
        mock_check.assert_called_once_with(path=test.path)
        self.assertEqual(mock_local_file_object.return_value.read.return_value, out_come)

    @patch("monolith_filemanager.adapters.local_file_processes.open")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_read_raw_file(self, mock_init, mock_check, mock_open):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()

        out_come = test.read_raw_file()
        mock_check.assert_called_once_with(path=test.path)
        mock_open.assert_called_once_with(test.path, "rb")
        mock_file_returned = mock_open.return_value.__enter__.return_value
        self.assertEqual(mock_file_returned.read.return_value, out_come)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_custom_read_file(self, mock_init, mock_check):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        test.path.file_type = "not pickle"
        custom_read_function = MagicMock(name='read function')
        data_output = MagicMock(name='data')
        custom_read_function.return_value = data_output

        out_come = test.custom_read_file(custom_read_function)
        mock_check.assert_called_once_with(path=test.path)
        custom_read_function.assert_called_once_with(test.path)
        self.assertEqual(out_come, data_output)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._create_directory_if_not_exists")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.local_file_object")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_write_file(self, mock_init, mock_local_file_object, mock_create_dir):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        mock_data = MagicMock()

        test.write_file(data=mock_data)
        mock_create_dir.assert_called_once()
        mock_local_file_object.return_value.write.assert_called_once_with(data=mock_data)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._create_directory_if_not_exists")
    @patch("monolith_filemanager.adapters.local_file_processes.open")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_write_raw_file(self, mock_init, mock_open, mock_create_dir):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        mock_data = MagicMock()

        test.write_raw_file(data=mock_data)
        mock_create_dir.assert_called_once()
        mock_open.assert_called_once_with(test.path, "wb")
        mock_file_returned = mock_open.return_value.__enter__.return_value
        mock_file_returned.write.assert_called_once_with(mock_data)

    @patch("monolith_filemanager.adapters.local_file_processes.os")
    @patch("monolith_filemanager.adapters.local_file_processes.shutil")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_delete_file_directory(self, mock_init, mock_check, mock_shutil, mock_os):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        mock_os.path = MagicMock()
        mock_os.path.isdir.return_value = True
        mock_os.path.isfile.return_value = False

        test.delete_file()
        mock_check.assert_called_once_with(path=test.path)
        mock_shutil.rmtree.assert_called_once_with(test.path)

    @patch("monolith_filemanager.adapters.local_file_processes.os")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.check_local_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_delete_file_single(self, mock_init, mock_check, mock_os):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()
        mock_os.path = MagicMock()
        mock_os.path.isdir.return_value = False
        mock_os.path.isfile.return_value = True

        test.delete_file()
        mock_check.assert_called_once_with(path=test.path)
        mock_os.remove.assert_called_once_with(test.path)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.delete_file")
    def test_delete_folder(self, mock_delete_file):
        mock_delete_file.return_value = None
        self.test_folder.delete_folder()
        mock_delete_file.assert_called_once_with(path=self.test_folder.path)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._create_directory_if_not_exists")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.increment_files")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isfile")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isdir")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_write_stream(self, mock_init, mock_os_path_isdir, mock_os_path_isfile, mock_increment_files,
                          mock_create_dir):
        # test if name taken
        mock_init.return_value = None
        mock_os_path_isdir.return_value = True
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = "mock/path/folder/file.txt"
        mock_stream = MagicMock()

        with self.assertRaises(LocalProcessesAdapterError):
            test.write_stream(stream=mock_stream)

        # test file exists so increment
        mock_os_path_isdir.return_value = False
        mock_os_path_isfile.return_value = True
        self.assertEqual("file.txt", test.write_stream(stream=mock_stream))
        mock_increment_files.assert_called_once_with()
        mock_create_dir.assert_called_once()
        mock_stream.save.assert_called_once_with(test.path)

        # test file does not exist, no increment
        mock_os_path_isdir.return_value = False
        mock_os_path_isfile.return_value = False
        mock_create_dir.reset_mock()
        mock_stream.reset_mock()
        self.assertEqual("file.txt", test.write_stream(stream=mock_stream))
        mock_create_dir.assert_called_once()
        mock_stream.save.assert_called_once_with(test.path)

    @patch("monolith_filemanager.adapters.local_file_processes.os.path.exists")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_increment_files(self, mock_init, mock_exists):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = "mock/path/folder/file.txt"
        mock_exists.return_value = False
        test.increment_files()
        self.assertEqual("mock/path/folder/file 2.txt", test.path)

        test.path = "mock/path/folder/file.txt"
        mock_exists.side_effect = [True, False]
        test.increment_files()
        self.assertEqual("mock/path/folder/file 3.txt", test.path)

    @patch("monolith_filemanager.adapters.local_file_processes.os.makedirs")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.increment_folders")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isdir")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isfile")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.dirname")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_create_directory_if_not_exists(self, mock_init, mock_os_path_dirname, mock_os_path_is_file,
                                            mock_os_path_is_dir, mock_increment_folders, mock_os_makedirs):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = "mock/pardir/folder/file"
        # test if name taken
        mock_os_path_dirname.side_effect = ["mock/pardir/folder", "mock/pardir"]
        mock_os_path_is_file.return_value = True
        with self.assertRaises(LocalProcessesAdapterError):
            test.create_directory_if_not_exists()

        # test if doesn't exist
        mock_os_path_is_file.return_value = False
        mock_os_path_is_dir.return_value = False
        mock_os_path_dirname.side_effect = ["mock/pardir/folder", "mock/pardir"]
        self.assertEqual("folder", test.create_directory_if_not_exists())
        mock_os_makedirs.assert_called_once_with("mock/pardir/folder")

        # test if already exists
        mock_os_path_is_file.return_value = False
        mock_os_path_is_dir.return_value = True
        mock_increment_folders.return_value = "folder 2"
        mock_os_path_dirname.side_effect = ["mock/pardir/folder", "mock/pardir"]
        self.assertEqual("folder 2", test.create_directory_if_not_exists())
        mock_increment_folders.assert_called_once_with(dirname="mock/pardir/folder")

    @patch("monolith_filemanager.adapters.local_file_processes.os.makedirs")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.exists")
    def test_increment_folders(self, mock_os_path_exists, mock_os_makedirs):
        mock_dirname = "mock/pardir/folder"
        mock_os_path_exists.return_value = False
        LocalFileProcessesAdapter.increment_folders(dirname=mock_dirname)
        mock_os_makedirs.assert_called_once_with("mock/pardir/folder 2")

        mock_os_makedirs.reset_mock()
        mock_os_path_exists.side_effect = [True, False]
        LocalFileProcessesAdapter.increment_folders(dirname=mock_dirname)
        mock_os_makedirs.assert_called_once_with("mock/pardir/folder 3")

    @patch("monolith_filemanager.adapters.local_file_processes.os.path")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_exists(self, mock_init, mock_os_path):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = MagicMock()

        test.exists()
        mock_os_path.exists.assert_called_once_with(test.path)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._get_file_info")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.join")
    @patch("monolith_filemanager.adapters.local_file_processes.os.walk")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_ls(self, mock_init, mock_os_walk, mock_os_path_join, mock_get_file_info):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test path", caching=MagicMock())
        test.path = "mock/path"
        mock_os_walk.return_value = iter([["mock/root", ["dir1", "dir2"], ["file1.txt"]]])
        mock_os_path_join.return_value = "mock/path/file1.txt"
        mock_get_file_info.return_value = "last_mod_date", 100

        self.assertEqual(({"file1.txt": {"last_modified": "last_mod_date", "size": 100}}, ["dir1", "dir2"]), test.ls())

    @patch("monolith_filemanager.adapters.local_file_processes.os.path.getsize")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.getmtime")
    def test__get_file_info(self, mock_path_getmtime, mock_path_get_size):
        mock_file = MagicMock()
        mock_path_getmtime.return_value = 0
        mock_path_get_size.return_value = 100
        self.assertEqual(('1970-01-01 00:00:00', 100), LocalFileProcessesAdapter._get_file_info(mock_file))

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.delete_file")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.__init__")
    def test_batch_delete(self, mock_init, mock_delete_file):
        mock_init.return_value = None
        test = LocalFileProcessesAdapter(file_path="test/path", caching=MagicMock())
        test.path = "test/path"
        test.path = "mock/folder/path"
        mock_paths = ["mock_folder", "mock_file"]
        mock_delete_file.side_effect = [None, None]
        test.batch_delete(paths=mock_paths)
        mock_delete_file.assert_has_calls = [call(path=test.path + mock_paths[0]),
                                             call(path=test.path + mock_paths[1])]

    @patch("monolith_filemanager.adapters.local_file_processes.os.rename")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.splitext")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.dirname")
    def test_rename_file(self, mock_os_dirname, mock_os_splitext, mock_exists, mock_os_rename):
        new_name = "new_file"
        mock_os_dirname.return_value = "/".join(self.test_file.path.split("/")[:-1])
        mock_os_splitext.return_value = ["mock/folder/test", ".xlsx"]
        mock_exists.side_effect = [True, False]

        new_path = "/".join(self.test_file.path.split("/")[:-1]) + f"/{new_name}" + mock_os_splitext.return_value[-1]
        self.test_file.rename_file(new_name=new_name)
        mock_os_rename.assert_called_once_with(self.test_file.path, new_path)

    @patch("monolith_filemanager.adapters.local_file_processes.os.rename")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.exists")
    @patch("monolith_filemanager.adapters.local_file_processes.os.walk")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.dirname")
    def test_rename_folder(self, mock_os_dirname, mock_os_walk, mock_exists, mock_rename):
        new_name = "new_folder"
        mock_os_dirname.return_value = "/".join(self.test_folder.path.split("/")[:-1])
        mock_os_walk.return_value = iter([["mock/root", ["dir1", "dir2"], ["file1.txt"]]])
        mock_exists.side_effect = [True, False]

        new_path = "/".join(self.test_folder.path.split("/")[:-1]) + f"/{new_name}"
        self.test_folder.rename_file(new_name=new_name)
        mock_rename.assert_called_once_with(self.test_folder.path, new_path)

    @patch("monolith_filemanager.adapters.local_file_processes.os.rename")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.exists")
    def test__move(self, mock_exists, mock_os_rename):
        mock_exists.return_value = False
        mock_os_rename.return_value = None
        mock_new_path = MagicMock()
        self.test_folder._move(mock_new_path)
        mock_os_rename.assert_called_once_with(self.test_folder.path, mock_new_path)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._move")
    @patch("monolith_filemanager.adapters.local_file_processes.FilePath")
    def test_move_file(self, mock_file_path, mock_move):
        mock_file_path.return_value = MagicMock()
        mock_move.return_value = None
        mock_destination_folder = "mock/destination/folder"
        self.test_file.move_file(f"{mock_destination_folder}")
        mock_file_path.assert_called_once_with(f"{mock_destination_folder}/{self.test_file.path.split('/')[-1]}")
        mock_move.assert_called_once_with(new_path=mock_file_path.return_value)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter._move")
    @patch("monolith_filemanager.adapters.local_file_processes.FilePath")
    def test_move_folder(self, mock_file_path, mock_move):
        mock_file_path.return_value = MagicMock()
        mock_move.return_value = None
        mock_destination_folder = "mock/destination/folder"
        self.test_folder.move_file(f"{mock_destination_folder}")
        mock_file_path.assert_called_once_with(f"{mock_destination_folder}/{self.test_folder.path.split('/')[-1]}")
        mock_move.assert_called_once_with(new_path=mock_file_path.return_value)

    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.move_folder")
    @patch("monolith_filemanager.adapters.local_file_processes.LocalFileProcessesAdapter.move_file")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isdir")
    @patch("monolith_filemanager.adapters.local_file_processes.os.path.isfile")
    @patch("monolith_filemanager.adapters.local_file_processes.FilePath")
    def test_batch_move(self, mock_filepath, mock_os_isfile, mock_os_isdir, mock_move_file, mock_move_folder):
        mock_paths = ["test.xlsx", "test_folder"]
        mock_destination_folder = "mock/destination/folder"
        mock_filepath.side_effect = [MagicMock(), MagicMock()]
        mock_os_isfile.side_effect = [True, False]
        mock_os_isdir.side_effect = [False, True]
        mock_move_file.return_value = None
        mock_move_folder.return_value = None

        self.test_folder.batch_move(paths=mock_paths, destination_folder=mock_destination_folder)
        mock_filepath.assert_has_calls([call(f"{self.test_folder.path}/{mock_paths[0]}"),
                                        call(f"{self.test_folder.path}/{mock_paths[1]}")])
        mock_move_file.assert_called_once_with(destination_folder=mock_destination_folder)
        mock_move_folder.assert_called_once_with(destination_folder=mock_destination_folder)


if __name__ == "__main__":
    main()
