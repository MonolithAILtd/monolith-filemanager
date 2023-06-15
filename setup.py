import setuptools
from setuptools import find_packages
from setuptools.command.build_py import build_py as build_py_orig

from requirements_manager import RequirementsManager, OperatorEnum

extras_packages = {
    "flask": ["flask", "tensorflow", "boto3", "protobuf", "jinja2", "itsdangerous", "werkzeug",
              "markupsafe"],
    "3d": ["pyvista", "cqkit", "cadquery"],
    "matlab": ["scipy"]
}

__version__ = '2.0.0'

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

requirements = RequirementsManager()


setuptools.setup(
    name="monolith_filemanager",
    version=__version__,
    author="Maxwell Flitton",
    author_email="maxwell@gmail.com",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    install_requires=requirements.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL),
    extras_require={
        'flask': requirements.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["flask"]),
        '3d': requirements.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["3d"]),
        'matlab': requirements.get_packages(operator=OperatorEnum.GREATER_THAN_EQUAL, extras_require=extras_packages["matlab"])
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
