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
        "aiofiles",
        "SQLAlchemy>=1.4.0",
        "httpx",
        "click",
        "jinja2",
        "sqlalchemy-utils",
        # @piercefreeman 02/16/2021 - required until we refactor async code
        # into microcosm-postgres and microcosm-pubsub
        "microcosm-pubsub",
        "microcosm-postgres",
        "asyncpg",
    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "app = microcosm_fastapi.factories.fastapi:configure_fastapi",
            "postgres_async = microcosm_fastapi.database.postgres:configure_postgres",
            "session_manager = microcosm_fastapi.database.session_manager:configure_session_manager",
            "sqs_message_dispatcher_async = microcosm_fastapi.pubsub.dispatcher:SQSMessageDispatcherAsync",
            # Conventions
            "documentation_convention = microcosm_fastapi.factories.docs:configure_docs",
            "build_info_convention = microcosm_fastapi.conventions.build_info.route:configure_build_info",
            "health_convention = microcosm_fastapi.conventions.health.route:configure_health",
            "config_convention = microcosm_fastapi.conventions.config.route:configure_config",
            "landing_convention = microcosm_fastapi.conventions.landing.route:configure_landing",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.9.0",
    ],
)
