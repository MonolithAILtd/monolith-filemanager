from unittest import TestCase, main
from unittest.mock import patch
from monolith_filemanager.file.mimp_file import MimpFile


class TestMimpFile(TestCase):

    @patch("monolith_filemanager.file.mimp_file.File.__init__")
    def test___init__(self, mock_init):
        mock_init.return_value = None
        test = MimpFile(path="test.mimp")
        mock_init.assert_called_once_with(path="test.mimp")
        self.assertEqual(None, test.header)
        self.assertEqual(None, test.version)
        self.assertEqual(None, test.steps)

    def test_format_data(self):
        test_data = "test"
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("<class 'str'> supplied as opposed to dict", str(context.exception))

        test_data = {}
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("header was not supplied", str(context.exception))

        test_data = {"header": {}}
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("version was not supplied in header", str(context.exception))

        test_data = {"header": {"version": 1}}
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("steps not supplied", str(context.exception))

        test_data = {"header": {"version": 1}, "steps": "test"}
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("steps should be a list instead of <class 'str'>", str(context.exception))

        test_data = {"header": {"version": 1}, "steps": [{}, "test"]}
        with self.assertRaises(Exception) as context:
            MimpFile.format_data(data=test_data)
        self.assertEqual("all steps need to be dicts", str(context.exception))

        test_data = {"header": {"version": 1}, "steps": [{}, {}], "something else": "this is something else"}
        self.assertEqual({"header": {"version": 1}, "steps": [{}, {}]}, MimpFile.format_data(data=test_data))

    @patch("monolith_filemanager.file.mimp_file.File.__init__")
    @patch("monolith_filemanager.file.mimp_file.msgpack")
    @patch("monolith_filemanager.file.mimp_file.MimpFile.format_data")
    @patch("monolith_filemanager.file.mimp_file.open")
    def test_read(self, mock_open, mock_format_data, mock_msgpack, mock_init):
        mock_init.return_value = None
        test = MimpFile(path="test.mimp")
        test.path = "test.mimp"
        outcome = test.read()

        mock_open.assert_called_once_with("test.mimp")
        mock_msgpack.unpack.assert_called_once_with(mock_open.return_value.__enter__.return_value)
        mock_format_data.assert_called_once_with(data=mock_msgpack.unpack.return_value)

        self.assertEqual(mock_format_data.return_value.__getitem__.return_value, test.header)
        self.assertEqual(mock_format_data.return_value.__getitem__.return_value.__getitem__.return_value, test.version)
        self.assertEqual(mock_format_data.return_value.__getitem__.return_value, test.steps)
        self.assertEqual(mock_format_data.return_value, outcome)

    @patch("monolith_filemanager.file.mimp_file.File.__init__")
    @patch("monolith_filemanager.file.mimp_file.msgpack")
    @patch("monolith_filemanager.file.mimp_file.MimpFile.format_data")
    @patch("monolith_filemanager.file.mimp_file.open")
    def test_write(self, mock_open, mock_format_data, mock_msgpack, mock_init):
        mock_init.return_value = None
        test = MimpFile(path="test.mimp")
        test.path = "test.mimp"
        outcome = test.write(data="test data")

        mock_format_data.assert_called_once_with(data="test data")
        mock_open.assert_called_once_with("test.mimp", "wb")
        mock_msgpack.pack.assert_called_once_with(mock_format_data.return_value,
                                                  mock_open.return_value.__enter__.return_value)
        self.assertEqual(None, outcome)


if __name__ == "__main__":
    main()
