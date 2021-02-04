#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-fastapi"
version = "1.0.0"


setup(
    name=project,
    version=version,
    description="Opinionated microservice API with FastAPI",
    #long_description=open("README.md").read(),
    #long_description_content_type="text/markdown",
    author="Pierce Freeman",
    author_email="pierce.freeman@globality.com",
    url="https://github.com/piercefreeman/microcosm-fastapi",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "microcosm>=3.0.0",
        "fastapi",
        "uvicorn",
    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "app = microcosm_fastapi.factories.fastapi:configure_fastapi",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.9.0",
    ],
)