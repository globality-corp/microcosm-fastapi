import pytest
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    is_,
)

from microcosm_fastapi.conventions.crud import configure_crud
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation

from microcosm_fastapi.tests.conventions.fixtures import (
    PERSON_ID_1,
    PERSON_ID_2,
    Person,
    person_create,
    person_delete,
    person_retrieve,
    person_search,
    person_update, PERSON_1,
)


PERSON_MAPPINGS = {
    Operation.Create: person_create,
    Operation.Delete: person_delete,
    Operation.Retrieve: person_retrieve,
    Operation.Search: person_search,
    Operation.Update: person_update,
}


class TestCRUD:

    @pytest.fixture
    def base_fixture(self, base, test_graph):
        person_ns = Namespace(subject=Person, version="v1")
        configure_crud(test_graph, person_ns, PERSON_MAPPINGS)
        base.add_attrs(
            person_id_1=PERSON_ID_1,
            person_id_2=PERSON_ID_2,
            base_url="/api/v1/person",
        )
        return base

    @pytest.mark.asyncio
    async def test_retrieve(self, client, test_graph, base_fixture):
        uri = f"{base_fixture.base_url}/{base_fixture.person_id_1}"
        response = await client.get(uri)
        assert_that(response.status_code, is_(equal_to(200)))

        assert_that(
            response.json(),
            has_entries(
                firstName=PERSON_1.first_name,
                lastName=PERSON_1.last_name,
                id=str(base_fixture.person_id_1),
            ),
        )

    @pytest.mark.asyncio
    async def test_retrieve_not_found(self, client, test_graph, base_fixture):
        test_graph.use("global_exception_handler")

        uri = f"{base_fixture.base_url}/{base_fixture.person_id_2}"
        response = await client.get(uri)
        assert_that(response.status_code, is_(equal_to(404)))

        assert_that(
            response.json(),
            has_entries(
                message='Person not found',
            ),
        )

    @pytest.mark.asyncio
    async def test_search(self, client, test_graph, base_fixture):
        uri = f"{base_fixture.base_url}"
        response = await client.get(uri)
        assert_that(response.status_code, is_(equal_to(200)))

        assert_that(
            response.json(),
            has_entries(
                offset=0,
                limit=20,
            ),
        )

        assert_that(
            response.json()['items'][0],
            has_entries(
                firstName=PERSON_1.first_name,
                lastName=PERSON_1.last_name,
                id=str(base_fixture.person_id_1),
            ),
        )

    @pytest.mark.asyncio
    async def test_create(self, client, test_graph, base_fixture):
        request_data = {
            "firstName": "Bob",
            "lastName": "Jones",
        }
        response = await client.post(base_fixture.base_url, json=request_data)

        assert_that(response.status_code, is_(equal_to(201)))

        assert_that(
            response.json(),
            has_entries(
                firstName=request_data["firstName"],
                lastName=request_data["lastName"],
                id=str(base_fixture.person_id_2),
            ),
        )

    @pytest.mark.asyncio
    async def test_update(self, client, test_graph, base_fixture):
        uri = f"{base_fixture.base_url}/{base_fixture.person_id_1}"

        request_data = {
            "firstName": "Bob",
        }
        response = await client.patch(uri, json=request_data)
        assert_that(response.status_code, is_(equal_to(200)))

        assert_that(
            response.json(),
            has_entries(
                firstName=request_data["firstName"],
                lastName=PERSON_1.last_name,
                id=str(base_fixture.person_id_1),
            ),
        )

    @pytest.mark.asyncio
    async def test_delete(self, client, test_graph, base_fixture):
        uri = f"{base_fixture.base_url}/{base_fixture.person_id_1}"

        response = await client.delete(uri)
        assert_that(response.status_code, is_(equal_to(204)))
