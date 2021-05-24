from unittest import TestCase, main
from unittest.mock import patch

from monolith_filemanager.file.keras_model_file import KerasModelFile


class TestKerasModelFile(TestCase):

    @patch("monolith_filemanager.file.keras_model_file.File.__init__")
    def test___init__(self, mock_file_init):
        mock_file_init.return_value = None
        KerasModelFile(path="test")
        mock_file_init.assert_called_once_with(path="test")

    @patch("tensorflow.keras.models.load_model")
    @patch("monolith_filemanager.file.keras_model_file.KerasModelFile.__init__")
    def test_read_file(self, mock_init, mock_load_model):
        mock_init.return_value = None
        test = KerasModelFile(path="test")
        test.path = "/some/path.keras_model"
        test.read()

        mock_init.assert_called_once_with(path="test")
        mock_load_model.assert_called_once_with("/some/path.keras_model", compile=False, custom_objects={})

    @patch("tensorflow.keras.models.save_model")
    @patch("monolith_filemanager.file.keras_model_file.KerasModelFile.__init__")
    def test_write_file(self, mock_init, mock_save_model):
        mock_init.return_value = None

        test = KerasModelFile(path="test")
        test.path = "/some/path.keras_model"
        test.write(data="string object")

        mock_init.assert_called_once_with(path="test")
        mock_save_model.assert_called_once_with("string object", "/some/path.keras_model", include_optimizer=False,
                                                save_format="h5")


if __name__ == "__main__":
    main()
