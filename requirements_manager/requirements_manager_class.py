import os.path
from typing import Dict, List, Optional
import configparser
from configparser import SectionProxy, ConfigParser

from .errors import NoPackagesInPipfileError, PipfilePathDoesNotExistError
from .operator_enums import OperatorEnum


# todo - Store this as a Github gist or re-usable, cross-repo package that can be used across Monolith projects

class RequirementsManager:
    """
    Manages reading the Pipfile and converting it into a correctly formatted list of strings for use in the
    'install_requires' and 'extra_requires' args of the setup process.

    Attributes:
        self.config: (Dict) list of raw line by line output of Pipfile
        self.packages: (Optional[Dict]) all packages and versions excl. dev-packages
        self.dev_packages: (Optional[Dict]) all dev-packages
    """
    def __init__(self, pipfile_loc: str = "./Pipfile") -> None:
        """
        :param pipfile_loc: (str) location of Pipfile
        :return: None
        :raises: (PipfilePathDoesNotExistError) if Pipfile path does not exist
        """
        if not os.path.exists(pipfile_loc):
            raise PipfilePathDoesNotExistError()
        self.config: ConfigParser = configparser.ConfigParser()
        self.config.read(pipfile_loc)
        self.packages: Optional[Dict] = None
        self.dev_packages: Optional[Dict] = None
        self._set_package_dicts()

    @staticmethod
    def _simplify_section(section: SectionProxy) -> Dict:
        """
        Parses each line of section from self.config Pipfile into dict with the following format:
        {<package_name>: >version>,...}
        :param section: (SectionProxy) proxy of config file section data
        :return: (Dict) key = package name, value = version
        """
        def _simplify_value(key):
            value = eval(section[key].replace("{", "dict(").replace("}", ")"))
            return '%s%s' % (key, section[key].strip('"')) if isinstance(value, str) \
                else '%s[%s]%s' % (key, value['extras'][0], value['version'])
        package_list = list(map(_simplify_value, section))
        return {package.split("==")[0]: package.split("==")[1] for package in package_list}

    def _set_package_dicts(self) -> None:
        """
        Sets the packages and dev_packages attributes from their sections in the self.config.
        :return: None
        :raises: (NoPackagesInPipfileError) If not packages found in self.config 'packages'
        """
        self.packages = self._simplify_section(self.config["packages"])
        if self.packages == {}:
            raise NoPackagesInPipfileError()
        self.dev_packages = self._simplify_section(self.config["dev-packages"])

    def get_packages(self, operator: OperatorEnum, extras_require: Optional[List[str]] = None) -> List[str]:
        """
        Get list of packages with correct version and given operator.
        :param operator: (OperatorEnum) e.g. '==' or '>='
        :param extras_require: (Optional[List[str]]) list of package names to exclusively return with version
        :return: (List[str]) e.g. [package==version,...]
        """
        if extras_require:
            return [f"{package}{operator.value}{version}" for package, version in self.packages.items() if package in
                    extras_require]
        else:
            return [f"{package}{operator.value}{version}" for package, version in self.packages.items()]

    def get_dev_packages(self, operator: OperatorEnum) -> List[str]:
        """
        Get list of dev-packages with correct version and given operator.
        :param operator: (OperatorEnum) e.g. '==' or '>='
        :return: (List[str]) e.g. [package==version,...]
        """
        return [f"{package}{operator.value}{version}" for package, version in self.dev_packages.items()]
