import pytest

from microcosm_fastapi.conventions.crud import configure_crud
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation

from microcosm_fastapi.tests.conventions.fixtures import (
    PERSON_ID_1,
    PERSON_ID_2,
    Person,
    person_create,
    person_delete,
    person_delete_batch,
    person_replace,
    person_retrieve,
    person_search,
    person_update,
    person_update_batch,
)


PERSON_MAPPINGS = {
    Operation.Create: person_create,
    Operation.Delete: person_delete,
    Operation.DeleteBatch: person_delete_batch,
    Operation.UpdateBatch: person_update_batch,
    Operation.Replace: person_replace,
    Operation.Retrieve: person_retrieve,
    Operation.Search: person_search,
    Operation.Update: person_update,
}


class TestCRUD:

    @pytest.fixture
    def base_fixture(self, base, test_graph):
        # test_graph.use("session_injection")
        person_ns = Namespace(subject=Person)
        configure_crud(test_graph, person_ns, PERSON_MAPPINGS)
        base.add_attrs(
            person_id_1=PERSON_ID_1,
            person_id_2=PERSON_ID_2,
        )

    @pytest.mark.asyncio
    async def test_retrieve(self, client, test_graph, base_fixture):

        response = await client.get(base_fixture.person_id_1)
        breakpoint()
        print()

    # @pytest.mark.asyncio
    # async def test_create(self, client, test_graph, base_fixture):