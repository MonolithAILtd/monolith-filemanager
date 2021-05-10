from unittest import TestCase, main
from unittest.mock import patch

from monolith_filemanager.file.yml_file import YmlFile, YamlFileError


class TestYmlFile(TestCase):

    @patch("monolith_filemanager.file.yml_file.File.__init__")
    def test___init__(self, mock_file):
        YmlFile(path="test")
        mock_file.assert_called_once_with(path="test")

    @patch("monolith_filemanager.file.yml_file.open")
    @patch("monolith_filemanager.file.yml_file.yaml")
    @patch("monolith_filemanager.file.yml_file.File.__init__")
    def test_read(self, mock_file, mock_yaml, mock_open):
        mock_file.return_value = None
        test = YmlFile(path="test")
        test.path = "test"
        out_come = test.read()

        mock_open.assert_called_once_with(str.encode("test"), 'rb')
        mock_open.return_value.close.assert_called_once_with()
        mock_yaml.load.assert_called_once_with(mock_open.return_value, Loader=mock_yaml.FullLoader)
        self.assertEqual(mock_yaml.load.return_value, out_come)

    @patch("monolith_filemanager.file.yml_file.open")
    @patch("monolith_filemanager.file.yml_file.yaml")
    @patch("monolith_filemanager.file.yml_file.File.__init__")
    def test_write(self, mock_file, mock_yaml, mock_open):
        mock_file.return_value = None
        test = YmlFile(path="test")
        data = {"one": 1, "two": 2}
        test.path = "test"
        test.write(data=data)

        mock_open.assert_called_once_with(str.encode("test"), 'w')
        mock_yaml.dump.assert_called_once_with(data, mock_open.return_value)
        mock_open.return_value.close.assert_called_once_with()

        with self.assertRaises(YamlFileError) as context:
            test.write(data="test")

        self.assertEqual("<class 'str'> data supplied instead of dict", str(context.exception))
        mock_open.assert_called_once_with(str.encode("test"), 'w')
        mock_yaml.dump.assert_called_once_with(data, mock_open.return_value)
        mock_open.return_value.close.assert_called_once_with()


if __name__ == "__main__":
    main()
