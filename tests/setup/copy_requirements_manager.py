from typing import List, Dict


class RequirementsManager:
    """
    Class to manage reading the Pipfile and converting it into a correctly formatted list of strings for use in the
    'install_requires' and 'extra_requires' args of the setup process.

    Attributes:
        self.pipfile: (Dict) list of raw line by line output of Pipfile
        self.package_index: (int) index of self.pipfile list for where package entries start
        self.dev_package_index: (int) index of self.pipfile list for where dev package entries start
        self.simple_package_dict: (Dict) dict to populate with package name keys with version values
        self.complex_package_dict: (Dict) as above attr however for packages specifying optional extras
    """
    def __init__(self, pipfile_loc: str):
        with open(pipfile_loc, "r") as pipfile:
            self.pipfile: List[str] = pipfile.read().split("\n")
        self.package_index: int = self.pipfile.index("[packages]")
        self.dev_package_index: int = self.pipfile.index("[dev-packages]")
        self.simple_package_dict: Dict = {}
        self.complex_package_dict: Dict = {}

    def parse_complex_pack(self, package_str: str) -> str:
        """
        Parse complex pipfile package with format e.g. dask = {version = "==2020.12.0", extras = ["complete"]} into
        string like "dask[complete]==2020.12.0".
        :param package_str: (str) complex pipfile format string
        """
        clean_list = [text.replace('"', '').replace("{", "").replace("}", "") for text in package_str.split(" = ")]
        stripped_list = [item.strip() for sublist in [x.split(",") for x in clean_list] for item in sublist]
        clean_package_str = stripped_list[0] + stripped_list[stripped_list.index("extras")+1] + \
                            stripped_list[stripped_list.index("version")+1]
        return clean_package_str

    def set_package_dicts(self) -> None:
        """
        Uses list of correctly formatted packages with versions to populate simple and complex package dict attributes
        with package name as key and version tag as value.
        """
        for package in self.get_simple_formatted_requirements():
            name = package.split("==")[0]
            version = package.split("==")[-1]
            self.simple_package_dict[name] = version

        for package in self.get_complex_formatted_requirements():
            name = package.split("==")[0]
            version = package.split("==")[-1]
            self.complex_package_dict[name] = version

    def get_simple_formatted_requirements(self) -> List[str]:
        """
        Parse simple packages into list of correctly formatted strings to match format of requirements.txt. e.g.
        [package1==0.0.1, package2==0.0.2]
        """
        return list(map(lambda x: x.replace(' = "', '')[:-1], self.simple_packages))

    def get_complex_formatted_requirements(self) -> List[str]:
        """
        Parse complex packages into list of correctly formatted strings to match format of requirements.txt. e.g.
        [package[complete]==0.0.1, package2[option]==0.0.2]
        """
        return list(map(self.parse_complex_pack, self.complex_packages))

    def get_loosened_requirements(self, filter: List[str] = None) -> List[str]:
        """
        If filter provided, then return a list of packages that match filter list with the version also specified
        loosely with >=.
        If no filter provided, return all packages and loosened version tag.
        """
        if self.simple_package_dict != {}:
            if filter:
                return [f"{name}>={version}" for name, version in {**self.simple_package_dict,
                                                                   **self.complex_package_dict}.items() if name in filter]
            else:
                return [f"{name}>={version}" for name, version in {**self.simple_package_dict,
                                                                   **self.complex_package_dict}.items()]

    @property
    def simple_packages(self) -> List[str]:
        """
        Return all packages from pipfile without optional extra features
        """
        return [package for package in self.pipfile[self.package_index + 1:self.dev_package_index - 1] if
                package.split(" = ")[1].startswith('"')]

    @property
    def complex_packages(self) -> List[str]:
        """
        Return all packages from pipfile with optional extra features
        """
        return [package for package in self.pipfile[self.package_index + 1:self.dev_package_index - 1] if
                package.split(" = ")[1].startswith('{')]
