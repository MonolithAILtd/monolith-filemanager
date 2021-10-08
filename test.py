

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


extras_packages = {
    "flask": ["flask", "tensorflow", "boto3"],
    "3d": ["pyvista", "gmsh"],
    "matlab": ["scipy"]
}

if __name__ == "__main__":
    reqs = RequirementsManager()
    reqs.set_package_dicts()
    print("install requires: ")
    packs = [item for sublist in extras_packages.values() for item in sublist]
    fin_packs = [pack.split(">=")[0] for pack in reqs.get_loosened_requirements() if pack not in packs]
    print(f"fin packs: {fin_packs}")
    print(reqs.get_loosened_requirements(filter=fin_packs))
    print("get flask packs: ")
    assert ["flask>=1.1.2", "tensorflow>=2.2.0", "boto3>=1.10.5"] == reqs.get_loosened_requirements(filter=extras_packages["flask"])
    print(reqs.get_loosened_requirements(filter=extras_packages["matlab"]))
    assert ["gmsh>=4.8.4", "pyvista>=0.24.2"] == reqs.get_loosened_requirements(filter=extras_packages["3d"])
    assert ["scipy>=1.4.1"] == reqs.get_loosened_requirements(filter=extras_packages["matlab"])
