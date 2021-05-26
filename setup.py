import pathlib

import setuptools
from setuptools import find_packages
from setuptools.command.build_py import build_py as build_py_orig


# from setuptools import dist
# dist.Distribution().fetch_build_eggs(['Cython==0.29'])
# from Cython.Build import cythonize


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

setuptools.setup(
    name="monolith_filemanager",
    version=version,
    author="Maxwell Flitton",
    author_email="maxwell@gmail.com",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    install_requires=[
        "gmsh>=4.2.0",
        "h5py<2.11.0,>=2.10.0",
        "joblib>=0.10.0",
        "scipy>=1.4.1",
        "numpy>=1.11.4",
        "pandas>=0.25.1",
        "pyvista>=0.24.2",
        "PyYAML>=4.1.2",
        "globre>=0.1.5",
        "dill>=0.2.8"
    ],
    extras_require={
     'flask': ["Flask>=1.0.0", "tensorflow>=2.1.0", "boto3>=1.16.43"]
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
