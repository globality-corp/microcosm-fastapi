"""
ServiceOfferingClassification CRUD routes.
"""
from microcosm.api import binding
from microcosm_fastapi.conventions.definition import EndpointDefinition
from microcosm_fastapi.conventions.crud import configure_crud
from microcosm_fastapi.operations import Operation
from microcosm_postgres.context import transactional


@binding("pizza_routes")
def configure_pizza_routes(graph):
    controller = graph.pizza_controller
    mappings = {
        Operation.Create: EndpointDefinition(
            func=transactional(controller.create),
            request_schema=NewServiceOfferingClassificationSchema(),
            response_schema=ServiceOfferingClassificationSchema(),
        ),
        Operation.Retrieve: EndpointDefinition(
            func=controller.retrieve,
            response_schema=ServiceOfferingClassificationSchema(),
        ),
        Operation.Search: EndpointDefinition(
            func=controller.search,
            request_schema=SearchServiceOfferingClassificationSchema(),
            response_schema=ServiceOfferingClassificationSchema(),
        ),
        Operation.Update: EndpointDefinition(
            func=transactional(controller.update_and_reencrypt),
            request_schema=UpdateServiceOfferingClassificationSchema(),
            response_schema=UpdatedServiceOfferingClassificationSchema(),
        ),
    }
    configure_crud(graph, controller.ns, mappings)
    return controller.ns