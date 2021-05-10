"""
This is a utility file that strips the git repos from the requirements and packages them in a requirements file for
github action builds for testing
"""


if __name__ == "__main__":
    private_package = []
    with open('requirements.txt', 'r') as requirements:
        buffer = requirements.read().split("\n")
        for requirement in buffer:
            if "git" in requirement:
                private_package.append(requirement)
                buffer.remove(requirement)

    with open('github_build_requirements.txt', 'w') as f:
        f.write('\n'.join(buffer))
    print("here is the packages being removed: {}".format(private_package))
    print("here is the buffer: {}".format(buffer))
