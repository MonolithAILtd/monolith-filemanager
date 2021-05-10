from unittest import TestCase, main
from unittest.mock import patch
from monolith_filemanager.file.base import File


class TestBase(TestCase):

    @patch.multiple(File, __abstractmethods__=set())
    @patch("monolith_filemanager.file.base.FilePath.__init__")
    def test___init__(self, mock_init):
        mock_init.return_value = None

        with self.assertRaises(Exception):
            File(path=1)

        input_path = "test"

        test = File(path=input_path)
        self.assertEqual(input_path, test.path)

        with patch("monolith_filemanager.file.base.isinstance") as mock_instance:
            mock_instance.return_value = True
            test = File(path=input_path)
            self.assertEqual(input_path, test.path)

        mock_init.assert_called_once_with(input_path)


if __name__ == "__main__":
    main()
