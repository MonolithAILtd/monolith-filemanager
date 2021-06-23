from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call
from monolith_filemanager.file import FileMap, Singleton


class TestFileMap(TestCase):

    @patch("monolith_filemanager.file.FileMap.init_bindings")
    def test___init__(self, mock_init_bindings):
        test = FileMap()
        test_two = FileMap()

        self.assertEqual(id(test), id(test_two))

        test["one"] = 1
        self.assertEqual(test, test_two)
        mock_init_bindings.assert_called_once_with()

        test = FileMap()
        Singleton._instances = {}
        test_two = FileMap()
        self.assertNotEqual(id(test), id(test_two))
        Singleton._instances = {}
        mock_init_bindings.assert_has_calls = [call(), call()]

    @patch("monolith_filemanager.file.FileMap.__init__")
    def test_add_binding(self, mock_init):
        mock_init.return_value = None
        test = FileMap()
        mock_file_object = MagicMock()
        mock_file_object.SUPPORTED_FORMATS = ["ext1", "ext2"]
        test.add_binding(file_object=mock_file_object)

        expected_outcome = {
            "ext1": mock_file_object,
            "ext2": mock_file_object
        }

        self.assertEqual(expected_outcome, test)

        mock_file_object_two = MagicMock()
        mock_file_object_two.SUPPORTED_FORMATS = ["ext3", "ext4"]

        test.add_binding(file_object=mock_file_object_two)

        expected_outcome = {
            "ext1": mock_file_object,
            "ext2": mock_file_object,
            "ext3": mock_file_object_two,
            "ext4": mock_file_object_two
        }

        self.assertEqual(expected_outcome, test)

        mock_file_object_three = MagicMock()
        mock_file_object_three.SUPPORTED_FORMATS = ["ext1"]

        with self.assertRaises(Exception):
            test.add_binding(file_object=mock_file_object_three)
        with self.assertRaises(Exception):
            test.add_binding(file_object=mock_file_object)

    def test_get_file(self):
        test = FileMap()
        test["csv"] = MagicMock()
        mock_path = MagicMock()
        mock_path.file_type = "csv"
        out_come = test.get_file(file_path=mock_path)
        self.assertEqual(test["csv"], out_come)

        mock_path.file_type = "test"
        with self.assertRaises(Exception):
            test.get_file(file_path=mock_path)


if __name__ == "__main__":
    main()
