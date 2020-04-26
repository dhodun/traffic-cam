import subprocess
from distutils.command.build import build as _build  # type: ignore

import setuptools

setuptools.setup(
    name='PACKAGE-NAME',
    version='PACKAGE-VERSION',
    install_requires=['numpy'],
    packages=setuptools.find_packages(),
)
