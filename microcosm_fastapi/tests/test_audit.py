"""
Audit structure tests.

"""
import logging
from types import SimpleNamespace

import pytest

from microcosm_fastapi.audit import (
    AuditOptions,
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
    person_update,
)

PERSON_MAPPINGS = {
    Operation.Create: person_create,
    Operation.Delete: person_delete,
    Operation.Retrieve: person_retrieve,
    Operation.Search: person_search,
    Operation.Update: person_update,
}


class TestAudit:
    """
    Test capturing of request data.

    """

    @pytest.fixture
    def base_fixture(self, test_graph):
        test_graph.use(
            "audit_middleware",
        )
        options = AuditOptions(
            include_request_body_status=True,
            include_response_body_status=True,
            include_path=True,
            include_query_string=True,
            log_as_debug=False,
        )
        person_ns = Namespace(subject=Person, version="v1")
        configure_crud(test_graph, person_ns, PERSON_MAPPINGS)
        sn = SimpleNamespace(
            person_id_1=PERSON_ID_1,
            person_id_2=PERSON_ID_2,
            base_url="/api/v1/person",
            options=options,
        )
        return sn

    @pytest.mark.asyncio
    async def test_log_request_id_header(self, client, test_graph, base_fixture, caplog):
        caplog.set_level(logging.INFO)
        request_id = "1234"
        uri = f"{base_fixture.base_url}/{base_fixture.person_id_1}"
        await client.get(uri, headers={"X-Request-Id": request_id})

        assert "X-Request-Id" in caplog.messages[0]
        assert "1234" in caplog.messages[0]
