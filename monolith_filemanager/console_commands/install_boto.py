import subprocess
import sys


def install_boto():
    """
    Installs the boto requirement for the package.

    Returns: None
    """
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'boto3>=1.16.43'])
