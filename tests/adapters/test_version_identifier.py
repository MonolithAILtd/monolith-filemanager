from unittest import TestCase, main

# from machine_learning.VERSION_ONE.model.compose.scaled_regressor import ScaledInputOutputRegressor
from monolith_filemanager.adapters.version_identifier import VersionIdentifierAdapter


class MlErrorGenerator:
    pass


class TestVersionIdentifierAdapter(TestCase):

    def test___init__(self):
        test = VersionIdentifierAdapter(path="path/to/file.txt", class_object=MlErrorGenerator)
        self.assertEqual("path/to/file.txt", test._path)
        self.assertEqual(MlErrorGenerator, test._class_object)

    def test_cleaned_path(self):

        # for non-versioned object
        test = VersionIdentifierAdapter(path="path/to/file.txt", class_object=MlErrorGenerator)
        self.assertEqual("path/to/file.txt", test.cleaned_path)

        test = VersionIdentifierAdapter(path="path/to/file.pickle", class_object=MlErrorGenerator)
        self.assertEqual("path/to/file.pickle", test.cleaned_path)


if __name__ == "__main__":
    main()
