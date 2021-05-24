import subprocess
import sys


def install_tensorflow():
    """
    Installs the tensorflow requirement for the package.

    Returns: None
    """
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tensorflow>=2.1.0'])
