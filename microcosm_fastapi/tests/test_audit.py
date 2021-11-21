"""
Audit structure tests.

"""
from logging import DEBUG, NOTSET, getLogger
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    is_not,
    none,
)
from microcosm.api import create_object_graph

from microcosm_fastapi.audit import (
    AuditOptions,
    RequestInfo,
    should_skip_logging,
)


PERSON_MAPPINGS = {
    Operation.Create: person_create,
    Operation.Delete: person_delete,
    Operation.Retrieve: person_retrieve,
    Operation.Search: person_search,
    Operation.Update: person_update,
}


class TestRequestInfo:
    """
    Test capturing of request data.

    """
    # def setup(self):
    #     self.graph = create_object_graph("example", testing=True, debug=True)
    #     self.graph.use(
    #         "audit_middleware",
    #     )
    #
    #     self.graph.flask.route("/")(test_func)
    #     self.graph.flask.route("/<foo>")(test_func)
    #
    #     self.options = AuditOptions(
    #         include_request_body=True,
    #         include_response_body=True,
    #         include_path=True,
    #         include_query_string=True,
    #         log_as_debug=False,
    #     )

    @pytest.fixture
    def base_fixture(self, base, test_graph):
        test_graph.use(
            "audit_middleware",
        )
        options = AuditOptions(
            include_request_body=True,
            include_response_body=True,
            include_path=True,
            include_query_string=True,
            log_as_debug=False,
        )

        base.add_attrs(
            options=options
        )
        return base

    def test_request_context(self):
        """
        Log entries can include context from headers.

        """
        with self.graph.flask.test_request_context("/", headers={"X-Request-Id": "request-id"}):
            request_info = RequestInfo(self.options, test_func, self.graph.request_context)
            dct = request_info.to_dict()
            request_id = dct.pop("X-Request-Id")
            assert_that(request_id, is_(equal_to("request-id")))
            assert_that(
                dct,
                is_(equal_to(dict(
                    operation="test_func",
                    method="GET",
                    func="test_func",
                ))),
            )


    def test_log_response_id_header(self):
        new_id = str(uuid4())
        with self.graph.flask.test_request_context("/"):
            request_info = RequestInfo(self.options, test_func, None)
            request_info.response_headers = {"X-FooBar-Id": new_id}

            logger = MagicMock()
            request_info.log(logger)
            logger.info.assert_called_with(dict(
                operation="test_func",
                method="GET",
                func="test_func",
                foo_bar_id=new_id,
            ))