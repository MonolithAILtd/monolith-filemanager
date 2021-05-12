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
    version="0.0.3",
    author="Maxwell Flitton",
    author_email="maxwell@gmail.com",
    description="Python package for reading and writing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/monolith-filemanager",
    install_requires=[
        "absl-py>=0.7.0",
        "appdirs>=1.1.3",
        "astunparse>=1.3.3",
        "boto3>=1.5.5",
        "botocore>=1.5.5",
        "cachetools>=3.1.1",
        "certifi>=2020.2.20",
        "chardet>=3.0.1",
        "click>=7.0.2",
        "dill>=0.1.9",
        "docutils>=0.10.2",
        "flake8>=3.5.3",
        "Flask>=1.0.0",
        "gast>=0.2.3",
        "globre>=0.1.0",
        "gmsh>=4.2.0",
        "google-auth>=1.11.2",
        "google-auth-oauthlib>=0.2.1",
        "google-pasta>=0.2.0",
        "grpcio>=1.32.0",
        "h5py>=2.5.0",
        "idna>=2.5",
        "imageio>=2.4.0",
        "importlib-metadata>=1.1.0",
        "install>=1.1.4",
        "itsdangerous>=1.1.0",
        "Jinja2>=2.5.2",
        "jmespath>=0.5.0",
        "joblib>=0.10.0",
        "Keras-Preprocessing>=1.1.2",
        "Markdown>=2.2.2",
        "MarkupSafe>=1.1.1",
        "mccabe>=0.3.1",
        "meshio>=3.0.10",
        "mock>=2.0.2",
        "msgpack>=1.0.0",
        "numpy>=1.11.4",
        "oauthlib>=2.1.0",
        "opt-einsum>=2.3.0",
        "pandas>=0.25.1",
        "Pillow>=5.0.0",
        "protobuf>=3.5.0",
        "pyasn1>=0.3.8",
        "pyasn1-modules>=0.2.8",
        "pycodestyle>=1.6.0",
        "pyflakes>=1.2.0",
        "python-dateutil>=2.3.1",
        "pytz>=2019.3",
        "pyvista>=0.24.2",
        "PyYAML>=4.1.2",
        "pyyml>=0.0.2",
        "redis>=2.5.3",
        "requests>=1.24.0",
        "requests-oauthlib>=1.3.0",
        "rsa>=3.6",
        "s3transfer>=0.2.1",
        "scipy>=1.4.1",
        "scooby>=0.5.2",
        "six>=1.5.0",
        "tensorboard>=1.2.2",
        "tensorboard-plugin-wit>=1.0.0",
        "tensorflow>=1.2.0",
        "tensorflow-estimator>=1.2.0",
        "termcolor>=1.1.0",
        "urllib3>=1.25.10",
        "vtk>=5.1.2",
        "Werkzeug>=1.0.1",
        "wrapt>=1.5.1",
        "zipp>=2.1.0",
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
