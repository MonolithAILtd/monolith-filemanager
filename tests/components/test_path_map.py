from unittest import TestCase, main

from monolith_filemanager.components.path_map import PathMap


class TestPathMap(TestCase):

    def test___init__(self):
        input_dict = {"one": "1", "two": "2", "three": "3"}
        test = PathMap(file_map=input_dict)
        self.assertEqual(input_dict, test)

    def test_map_path(self):
        test = PathMap(file_map={"one": "s3://1", "two": "2", "three": "3"})

        self.assertEqual("s3://1/to/path.txt", test.map_path(path="one/to/path.txt"))
        self.assertEqual("2/to/path.txt", test.map_path(path="two/to/path.txt"))
        self.assertEqual("3/to/path.txt", test.map_path(path="three/to/path.txt"))
        self.assertEqual("four/to/path.txt", test.map_path(path="four/to/path.txt"))


if __name__ == "__main__":
    main()
