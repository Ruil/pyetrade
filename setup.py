#!/usr/bin/env python3

from distutils.core import setup
from pyetrade import __version__

# requirements
with open("requirements.txt") as requirements:
    req = [i.strip() for i in requirements]
