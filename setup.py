import setuptools
from setuptools import find_packages
from setuptools.command.build_py import build_py as build_py_orig


extras_packages = {
    "flask": ["flask", "tensorflow", "boto3", "protobuf", "jinja2", "itsdangerous", "werkzeug",
              "markupsafe"],
    "3d": ["pyvista", "cqkit", "cadquery"],
    "matlab": ["scipy"]
}

__version__ = '3.2.0'

class CustomBuildPy(build_py_orig):
    """
    subclass build_py so that we collect no .py files inside the built pip package
    this is done by overriding build_packages method with a noop
    """
    def build_packages(self):
        pass


with open("README.md", "r") as fh:
    long_description = fh.read()

directives = {
    'language_level': 3,
    'always_allow_keywords': True
}


setuptools.setup(
    name="monolith_filemanager",
    version=__version__,
    author="Monolith AI",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    install_requires=[
        'h5py==2.10.0',
        'joblib>=0.15.0',
        'flask==1.1.4',
        'jinja2==2.11.3',
        'itsdangerous==1.1.0',
        'werkzeug==1.0.1',
        'MarkupSafe==2.0.1',
        'tensorflow==2.2.0',
        'protobuf==3.19.6',
        'numpy==1.22.4',
        'pandas==1.0.5',
        'dask[complete]==2020.12.0',
        'distributed==2021.1.1',
        'dill==0.2.9',
        'pyyaml==5.1.2',
        'boto3==1.10.5',
        'botocore==1.13.5',
        'requests==2.22.0',
        'openpyxl==3.0.7',
        'pyarrow==0.16.0',
        'xlwt==1.3.0',
        'xlrd==1.2.0',
        'scipy==1.4.1',
        'cqkit==0.5.1',
        'cadquery==2.2.0',
        's3fs==0.3.0',
    ],
    extras_require={
        'flask': extras_packages["flask"],
        '3d': extras_packages["3d"],
        'matlab': extras_packages["matlab"]
    },
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'file-hello = monolith_filemanager.console_commands.hello:print_logo',
            'file-install-flask = monolith_filemanager.console_commands.install_flask:install_flask',
            'file-install-tensorflow = monolith_filemanager.console_commands.install_tensorflow:install_tensorflow',
            'file-install-aws = monolith_filemanager.console_commands.install_boto:install_boto'
        ],
    }
)
