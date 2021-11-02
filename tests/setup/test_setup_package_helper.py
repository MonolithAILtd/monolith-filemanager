from unittest import TestCase

from tests.setup.copy_requirements_manager import RequirementsManager


extras_packages = {
    "flask": ["flask", "tensorflow", "boto3"],
    "3d": ["pyvista", "gmsh"],
    "matlab": ["scipy"]
}

"""
This test is included purely to demonstrate how the TestRequirementsManager class is working and that it correctly parses
a Pipfile into a format suitable for the setup.py install_requires and extras_require package list args.
"""

all_packages = ['globre>=0.1.5', 'h5py>=2.10.0', 'joblib>=0.15.0', 'flask>=1.1.2', 'gmsh>=4.8.4', 'tensorflow>=2.2.0',
                'numpy>=1.16.4', 'pandas>=0.25.1', 'distributed>=2021.1.1', 'dill>=0.2.9', 'pyvista>=0.24.2',
                'pyyaml>=5.1.2', 'boto3>=1.10.5', 'botocore>=1.13.5', 'requests>=2.22.0', 'openpyxl>=3.0.7',
                'pyarrow>=0.16.0', 'xlwt>=1.3.0', 'xlrd>=1.2.0', 'scipy>=1.4.1', 'dask[complete]>=2020.12.0']


class TestRequirementsManager(TestCase):

    def setUp(self) -> None:
        self.reqs = RequirementsManager(pipfile_loc="tests/resources/Pipfile")
        self.reqs.set_package_dicts()
        self.packs = [item for sublist in extras_packages.values() for item in sublist]
        self.fin_packs = [pack.split(">=")[0] for pack in self.reqs.get_loosened_requirements() if pack not in self.packs]

    def test_manager_output(self):
        self.assertEqual(all_packages, self.reqs.get_loosened_requirements(filter=self.fin_packs))
        self.assertEqual(["flask>=1.1.2", "tensorflow>=2.2.0", "boto3>=1.10.5"], self.reqs.get_loosened_requirements(
            filter=extras_packages["flask"]))
        self.assertEqual(["gmsh>=4.8.4", "pyvista>=0.24.2"], self.reqs.get_loosened_requirements(filter=extras_packages["3d"]))
        self.assertEqual(["scipy>=1.4.1"], self.reqs.get_loosened_requirements(filter=extras_packages["matlab"]))

