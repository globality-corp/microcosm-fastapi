import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient
from microcosm.object_graph import create_object_graph


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def graph():
    return create_object_graph(name="example", testing=True)


@pytest_asyncio.fixture(scope="function")
async def client(graph):
    async with AsyncClient(app=graph.app, base_url="http://localhost") as client:
        yield client


@pytest.fixture(scope="function")
def test_graph(graph):
    graph.sns_producer.sns_client.reset_mock()
    yield graph
