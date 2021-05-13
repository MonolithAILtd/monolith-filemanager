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

directives = {
    'language_level': 3,
    'always_allow_keywords': True
}

setuptools.setup(
    name="monolith_filemanager",
    version="0.0.7",
    author="Maxwell Flitton",
    author_email="maxwell@gmail.com",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    install_requires=[
        "gmsh>=4.5.6",
        "h5py>=3.0.0",
        "joblib>=1.0.0",
        "scipy>=1.6.0",
        "numpy>=1.19.0",
        "pandas>=1.1.5",
        "pyvista>=0.29.0",
        "PyYAML>=5.3",
        "globre>=0.1.5",
        "boto3>=1.16.43",
        "tensorflow>=2.1.0",
        "Flask>=1.0.0"
    ],
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
        ],
    }
    # ext_modules=cythonize("caching/**/*.py", exclude="tests/**/*.py", compiler_directives=directives, nthreads=4),
    # cmdclass={'build_py': CustomBuildPy},
    # include_package_data=False,
    # options={"bdist_wheel": {"universal": "1"}}
)
