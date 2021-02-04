#!/usr/bin/env python
from setuptools import find_packages, setup


project = "test_project"
version = "1.0.0"

setup(
    name=project,
    version=version,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "microcosm-postgres"
    ],
    entry_points={
        "console_scripts": [
            "runserver = test_project.main:runserver",
        ],
    },
)