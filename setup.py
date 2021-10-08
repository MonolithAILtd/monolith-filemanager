import pathlib

import setuptools
from setuptools import find_packages
from setuptools.command.build_py import build_py as build_py_orig


# from setuptools import dist
# dist.Distribution().fetch_build_eggs(['Cython==0.29'])
# from Cython.Build import cythonize

extras_packages = {
    "flask": ["flask", "tensorflow", "boto3"],
    "3d": ["pyvista", "gmsh"],
    "matlab": ["scipy"]
}


class RequirementsManager:
    def __init__(self):
        with open("./Pipfile", "r") as pipfile:
            self.pipfile = pipfile.read().split("\n")
        self.package_index = self.pipfile.index("[packages]")
        self.dev_package_index = self.pipfile.index("[dev-packages]")
        self.simple_package_dict = {}
        self.complex_package_dict = {}

    def parse_complex_pack(self, package_str: str):
        clean_list = [text.replace('"', '').replace("{", "").replace("}", "") for text in package_str.split(" = ")]
        stripped_list = [item.strip() for sublist in [x.split(",") for x in clean_list] for item in sublist]
        clean_package_str = stripped_list[0] + stripped_list[stripped_list.index("extras")+1] + \
                            stripped_list[stripped_list.index("version")+1]
        return clean_package_str

    def set_package_dicts(self):
        for package in self.get_simple_formatted_requirements():
            name = package.split("==")[0]
            version = package.split("==")[-1]
            self.simple_package_dict[name] = version

        for package in self.get_complex_formatted_requirements():
            name = package.split("==")[0]
            version = package.split("==")[-1]
            self.complex_package_dict[name] = version

    def get_simple_formatted_requirements(self):
        return list(map(lambda x: x.replace(' = "', '')[:-1], self.simple_packages))

    def get_complex_formatted_requirements(self):
        return list(map(self.parse_complex_pack, self.complex_packages))

    def get_loosened_requirements(self, filter: list = None):
        if self.simple_package_dict != {}:
            if filter:
                return [f"{name}>={version}" for name, version in {**self.simple_package_dict,
                                                                   **self.complex_package_dict}.items() if name in filter]
            else:
                return [f"{name}>={version}" for name, version in {**self.simple_package_dict,
                                                                   **self.complex_package_dict}.items()]

    @property
    def simple_packages(self):
        return [package for package in self.pipfile[self.package_index + 1:self.dev_package_index - 1] if
                package.split(" = ")[1].startswith('"')]

    @property
    def complex_packages(self):
        return [package for package in self.pipfile[self.package_index + 1:self.dev_package_index - 1] if
                package.split(" = ")[1].startswith('{')]


class CustomBuildPy(build_py_orig):
    """
    subclass build_py so that we collect no .py files inside the built pip package
    this is done by overriding build_packages method with a noop
    """
    def build_packages(self):
        pass


with open("README.md", "r") as fh:
    long_description = fh.read()

with open(str(pathlib.Path(__file__).parent.absolute()) + "/monolith_filemanager/version.py", "r") as fh:
    version = fh.read().split("=")[1].replace("'", "")

directives = {
    'language_level': 3,
    'always_allow_keywords': True
}

reqs = RequirementsManager()
reqs.set_package_dicts()

# handle generation of install_requires filtered packages
extra_packs = [item for sublist in extras_packages.values() for item in sublist]
install_requires = [pack.split(">=")[0] for pack in reqs.get_loosened_simple_requirements() if pack not in extra_packs]

setuptools.setup(
    name="monolith_filemanager",
    version=version,
    author="Maxwell Flitton",
    author_email="maxwell@gmail.com",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    # install_requires=[
    #     "h5py<2.11.0,>=2.10.0",
    #     "joblib>=0.16.0",
    #     "numpy>=1.16.4",
    #     "pandas>=0.25.1",
    #     "PyYAML>=5.1.2",
    #     "globre>=0.1.5",
    #     "dill>=0.2.9"
    # ],
    install_requires=install_requires,
    # extras_require={
    #     'flask': ["flask>=1.1.2", "tensorflow>=2.2.0", "boto3>=1.10.5"],
    #     '3d': ["pyvista>=0.24.2", "gmsh>=4.8.4"],
    #     'matlab': ["scipy>=1.4.1"]
    # },
    extras_require={
        'flask': reqs.get_loosened_simple_requirements(filter=extras_packages["flask"]),
        '3d': reqs.get_loosened_simple_requirements(filter=extras_packages["3d"]),
        'matlab': reqs.get_loosened_simple_requirements(filter=extras_packages["matlab"])
    },
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'file-hello = monolith_filemanager.console_commands.hello:print_logo',
            'file-install-flask = monolith_filemanager.console_commands.install_flask:install_flask',
            'file-install-tensorflow = monolith_filemanager.console_commands.install_tensorflow:install_tensorflow',
            'file-install-aws = monolith_filemanager.console_commands.install_boto:install_boto'
        ],
    }
    # ext_modules=cythonize("caching/**/*.py", exclude="tests/**/*.py", compiler_directives=directives, nthreads=4),
    # cmdclass={'build_py': CustomBuildPy},
    # include_package_data=False,
    # options={"bdist_wheel": {"universal": "1"}}
)
