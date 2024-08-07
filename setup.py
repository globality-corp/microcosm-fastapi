#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-fastapi"
version = "1.0.0"


setup(
    name=project,
    version=version,
    description="Opinionated microservice API with FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp//microcosm-fastapi",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.11",
    keywords="microcosm",
    install_requires=[
        "microcosm>=3.0.0",
        "fastapi",
        "uvicorn",
        "aiofiles",
        "SQLAlchemy[asyncio]>=1.4.0",
        "httpx",
        "h11<0.13", # @pierce 01-24-2022 pin because of httpx conflict
        "click",
        "jinja2",
        "sqlalchemy-utils",
        # @piercefreeman 02/16/2021 - required until we refactor async code
        # into microcosm-postgres and microcosm-pubsub
        "microcosm-pubsub>=3.0.0",
        "microcosm-postgres[encryption]>=4.0.0",
        "asyncpg",
        "psycopg2-binary>=2.7.5",
        "makefun",
        "pydantic<2.0.0",
        "greenlet",
    ],
    setup_requires=[
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "app = microcosm_fastapi.factories.fastapi:configure_fastapi",
            "postgres_async = microcosm_fastapi.database.postgres:configure_postgres",
            "session_maker_async = microcosm_fastapi.database.session:configure_session_maker",
            "sqs_message_dispatcher_async = microcosm_fastapi.pubsub.dispatcher:SQSMessageDispatcherAsync",
            # Conventions
            "documentation_convention = microcosm_fastapi.factories.docs:configure_docs",
            "build_info_convention = microcosm_fastapi.conventions.build_info.route:configure_build_info",
            "health_convention = microcosm_fastapi.conventions.health.route:configure_health",
            "config_convention = microcosm_fastapi.conventions.config.route:configure_config",
            "landing_convention = microcosm_fastapi.conventions.landing.route:configure_landing",
            "audit_middleware = microcosm_fastapi.audit:configure_audit_middleware",
            "request_context = microcosm_fastapi.context:configure_request_context",
            "global_exception_handler = microcosm_fastapi.exception_handler:configure_global_exception_handler",
            "logging_data_map = microcosm_fastapi.logging_data_map:configure_logging_data_map",
            "session_injection = microcosm_fastapi.session:configure_session_injection",
            "route_metrics = microcosm_fastapi.metrics:configure_route_metrics"
        ],
    },
    extras_require={
        "metrics": "microcosm-metrics>=3.0.0",
        "test": [
            "coverage>=3.7.1",
            "PyHamcrest>=1.9.0",
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "microcosm-metrics>=3.0.0",
        ],
        "typehinting": [
            "mypy",
            "types-pkg-resources",
            "types-requests",
            "types-setuptools"
        ],
        "lint": [
            "flake8",
            "flake8-print",
            "flake8-isort",
        ]
    }
)
