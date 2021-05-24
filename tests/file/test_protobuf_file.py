from unittest import TestCase, main
from unittest.mock import patch

from monolith_filemanager.file.protobuf_file import ProtobufFile


class TestProtobufFile(TestCase):

    @patch("monolith_filemanager.file.protobuf_file.File.__init__")
    def test___init__(self, mock_file_init):
        ProtobufFile(path="test")
        mock_file_init.return_value = None
        mock_file_init.assert_called_once_with(path="test")

    # @patch("monolith_filemanager.file.protobuf_file.tf")
    # @patch("monolith_filemanager.file.protobuf_file.ProtobufFile.__init__")
    # def test_read_file(self, mock_init, mock_tf):
    #     mock_init.return_value = None
    #     test = ProtobufFile(path="test")
    #     test.path = "/some/path.pb"
    #     test.read()
    #
    #     mock_init.assert_called_once_with(path="test")
    #
    #     mock_tf.io.gfile.GFile.assert_called_once_with("/some/path.pb", "rb")
    #     mock_tf.compat.v1.GraphDef.assert_called_once_with()
    #
    #     mock_file = mock_tf.io.gfile.GFile.return_value.__enter__.return_value
    #     mock_graph_def = mock_tf.compat.v1.GraphDef.return_value
    #
    #     mock_graph_def.ParseFromString.assert_called_once_with(mock_file.read.return_value)
    #
    # @patch("tensorflow.io.write_graph")
    # @patch("monolith_filemanager.file.protobuf_file.ProtobufFile.__init__")
    # def test_write_file(self, mock_init, mock_write_graph):
    #     mock_init.return_value = None
    #     test = ProtobufFile(path="test")
    #     test.path = "/some/path.pb"
    #     test.write(data="data object")
    #
    #     mock_init.assert_called_once_with(path="test")
    #
    #     mock_write_graph.assert_called_once_with(
    #         graph_or_graph_def="data object",
    #         logdir="/some",
    #         name="path.pb",
    #         as_text=False
    #     )


if __name__ == "__main__":
    main()
