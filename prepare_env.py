"""
Environment setup script for the H→ZZ*→4ℓ analysis.

Installs the `atlasopenmagic` package and configures the ATLAS Open Data
environment (authentication, cache directory, etc.) for the current Python
installation.

Run once before executing analysis.py:

    python prepare_env.py
"""

import subprocess
import sys

# Install the ATLAS Open Data helper library
subprocess.check_call([sys.executable, "-m", "pip", "install", "atlasopenmagic"])

from atlasopenmagic import install_from_environment
install_from_environment()
