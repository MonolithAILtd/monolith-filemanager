from unittest import TestCase

from requirements_manager import RequirementsManager, OperatorEnum
from requirements_manager.errors import NoPackagesInPipfileError, PipfilePathDoesNotExistError


extras_packages = {
    "flask": ["flask", "tensorflow", "boto3", "protobuf", "jinja2", "itsdangerous", "werkzeug",
              "markupsafe"],
    "3d": ["pyvista", "cqkit", "cadquery"],
    "matlab": ["scipy"]
}

flask_packages = ["flask>=1.1.4", "tensorflow>=2.2.0", "boto3>=1.10.5", "protobuf>=3.20.1",
                  "jinja2>=2.11.3", "itsdangerous>=1.1.0", "werkzeug>=1.0.1", "markupsafe>=2.0.1"]
three_d_packages = ["pyvista>=0.34.2", "cqkit>=0.5.1", "cadquery>=2.2.0"]
matlab_packages = ["scipy>=1.4.1"]

all_packages = ['h5py>=2.10.0', 'joblib>=0.15.0', 'numpy>=1.22.4', 'pandas>=1.2.5',
                'distributed>=2021.1.1', 'dill>=0.2.9', 'pyyaml>=5.1.2', 'boto3>=1.10.5', 'botocore>=1.13.5',
                'requests>=2.22.0', 'openpyxl>=3.0.7', 'pyarrow>=1.0.1', 'xlwt>=1.3.0', 'xlrd>=2.0.1',
                'dask[complete]>=2020.12.0', 's3fs>=0.3.0'] \
                    + flask_packages + three_d_packages + matlab_packages


class TestRequirementsManager(TestCase):
    """
    Simple functional Tests for RequirementsManager
    """

    def setUp(self) -> None:
        self.reqs = RequirementsManager(pipfile_loc="tests/resources/Pipfile")

    def test_pipfile_invalid_path(self):
        with self.assertRaises(PipfilePathDoesNotExistError):
            self.reqs = RequirementsManager(pipfile_loc="tests/resources/invalid")

    def test_manager_get_packages_success(self):
        assert set(all_packages) == set(self.reqs.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL))
        assert set(flask_packages) == set(
            self.reqs.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["flask"]))
        assert set(three_d_packages) == set(
            self.reqs.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["3d"]))
        assert set(matlab_packages) == set(
            self.reqs.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["matlab"]))

    def test_manager_get_packages_fail(self):
        # assert errors raised if 'packages' section of Pipfile contains no packages
        with self.assertRaises(NoPackagesInPipfileError):
            reqs_no_packages = RequirementsManager(pipfile_loc="tests/resources/Pipfile_no_packages")

