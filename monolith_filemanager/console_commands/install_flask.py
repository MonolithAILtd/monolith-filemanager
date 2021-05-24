import subprocess
import sys


def install_flask():
    """
    Installs the flask requirement for the package.

    Returns: None
    """
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask>=1.0.0'])
