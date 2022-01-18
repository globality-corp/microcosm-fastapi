# microcosm-fastapi

A bridge between FastAPI and microcosm. Provide state-of-the-art speed of hosting microservices in Python along with dependency injection.

## Top Features

- Async compliant protocol to add new microservice functions
- Specify API requests and responses with business-logic typehinting, while following strongly conventioned CRUD operations to access the database
- Async postgres support using the latest SQLAlchemy 1.4 (still in beta), to support more concurrent client users with fewer CPU blocking requests
- Automatic generation of interactive documentation, available on localhost:5000/docs when doing development work
- No telemetry: locally hosted documentation and other fastapi dependencies

## Migration from microcosm-flask

If you're using microcosm already, there's a high chance you're using `microcosm-flask` as your communication layer. This library attempts to give a relatively straightforward migration path from microcosm-flask by using the same abstraction and function names where possible. In order to truly leverage the best design decisions that went into FastAPI, however, we also need to refactor some of our logic into the new FastAPI paradigm.

### Resources

When defining resources in flask, you're likely used to defining a schema for everything that you'll ever need to serialize from client users. This includes `New` schemas for creating new objects, `Standard` schemas for retrieving objects from the database, and `Search` schemas for extracting the URL parameters that can search against the database layer. These are defined via `marshmallow` which provides the serialization layer to convert from json->python and python->json. Something like this:

```
from microcosm_flask.paging import PageSchema
from marshmallow import Schema, fields

class NewPizzaSchema(Schema):
    toppings = fields.String(required=True)

class PizzaSchema(NewPizzaSchema):
    id: fields.UUID(required=True)

class PizzaSearchSchema(PageSchema):
    toppings = fields.String(required=False)
```

Instead of marshmallow, FastAPI makes extensive use of `pydantic` to provide the validation layers. Pydantic is a more modern library in comparison. It uses python typehints in order to define expected field types and has more built-in functionality when compared to marshmallow. It's straightforward to convert the above definitions into ones that are pydantic compatible. Note that we remove the `PizzaSearchSchema` entirely because this definition will be specified in another file.

```
from microcosm_fastapi.conventions.schemas import BaseSchema
from uuid import UUID

class NewPizza(BaseSchema):
    toppings: str

class Pizza(NewPizza)
    id: UUID
```

Just like typehinting in standard python functions, arguments are required unless you specify an `Optional` flag alongside their type. This will enforce that client callers provide `toppings` when creating a new `Pizza`.

### Routes

In microcosm-flask, your routes are usually split between two files. You'll have `pizza/crud.py` and `pizza/controller.py`. The crud file specifies the supported operations and resources for the given namespace. The controller will implement any relevant business logic to transform the input client request before passing it to the backing store. Something like:

```
@binding("pizza_v1_routes")
def configure_pizza_routes(graph):
    controller = graph.credential_pack_controller

    mappings = {
        Operation.Create: EndpointDefinition(
            func=transactional(controller.create),
            request_schema=NewPizzaSchema(),
            response_schema=PizzaSchema(),
        ),
        Operation.Retrieve: EndpointDefinition(
            func=controller.retrieve, 
            response_schema=PizzaSchema(),
        ),
        Operation.Search: EndpointDefinition(
            func=controller.search,
            request_schema=SearchPizzaSchema(),
            response_schema=PizzaSchema(),
        ),
    }
    configure_crud(graph, controller.ns, mappings)

    return controller.ns
```

```
@binding("pizza_controller")
class PizzaController(CRUDStoreAdapter):
    def __init__(self, graph):
        super().__init__(graph, graph.pizza_store)
        self.ns = Namespace(subject=Pizza, version="v1")
```

One drawback with this approach is that a lot of the logic is abstracted away into the `CRUDStoreAdapter` and `configure_crud` code. It's not immediately transparent to new team members what the API functions will actually look like when they're created.

The goal in our new routing convention is to have one file the provides the full source of truth. This route will contain an explicit definition of all APIs that are available for the given database object. The typehinting of both the function and the response signatures are parsed by `microcosm-fastapi` for you - requests are validated against the function types and responses are serialized to fit within the return type annotation.

```
from microcosm_fastapi.conventions.crud import configure_crud
from microcosm_fastapi.conventions.crud_adapter import CRUDStoreAdapter
from microcosm_fastapi.conventions.schemas import SearchSchema

@binding("pizza_route")
class PizzaController(CRUDStoreAdapter):
    def __init__(self, graph):
        super().__init__(graph, graph.pizza_store)

        ns = Namespace(
            subject=Pizza,
            version="v1",
        )

        mappings = {
            Operation.Create: self.create,
            Operation.Retrieve: self.retrieve,
            Operation.Search: self.search,
        }
        configure_crud(graph, ns, mappings)

    async def create(self, pizza: NewPizzaSchema) -> PizzaSchema:
        return await super()._create(pizza)

    async def retrieve(self, pizza_id: UUID) -> PizzaSchema:
        return await super()._retrieve(pizza_id)

    async def search(self, limit: int = 20, offset: int = 0) -> SearchSchema(PizzaSchema):
        return await super()._search(limit=limit, offset=offset)
```

By convention, edge operations (ie. retrieve / patch / etc) will be passed the object UUID of interest automatically by microcosm-fastapi. This keyword argument is expected to be in the format of `{snake_case(namespace object)}_id`. See `retrieve` for an example here. Clients are still expected to typehint this accordingly as a UUID.

### Stores

We bundle an async-compatible postgres client alongside `microcosm-fastapi`. To see the maximum performance boosts, you'll need to upgrade your Store instances as well to be async compliant.

Any custom implemented functions must be `await` when calling the superclass.

```
from microcosm_fastapi.database.store import StoreAsync

@binding("pizza_store")
class PizzaStore(StoreAsync):
    def __init__(self, graph):
        super().__init__(graph, Pizza)

    async def create(self, pizza):
        pizza.delivery_date = datetime.now()
        return await super().create(pizza)
```

Include the following dependencies in your graph:

```
app.use(
    "postgres",
    "session_maker_async",
    "postgres_async",
)
```

### Other Application Changes

Create two new files `wsgi` and `wsgi_debug` to host the production and development graphs separately:

```
from annotation_jobs.app import create_app
graph = create_app()
app = graph.app
```

```
from annotation_jobs.app import create_app
graph = create_app(debug=True)
app = graph.app
```

Update your `main.py` to host:

```
from microcosm_fastapi.runserver import main as runserver_main

def runserver():
    # This graph is just used for config parameters
    graph = create_app(debug=True, model_only=True)

    runserver_main("{application_bundle}.wsgi_debug:app", graph)
```

### Misc Lookup

QueryStringList -> microcosm_fastapi.conventions.parsers.SeparatedList

## Test Project

We have set up a test project to demonstrate how the new API would look like when deployed within a service. To get started create a new DB:

```
createuser test_project
createdb -O test_project test_project_db
createdb -O test_project test_project_test_db
```

## Running Tests

```
pip install pytest pytest-cov pytest-asyncio

cd test-project
pytest test_project
```

## Bumping Versions

When you're ready to merge your PR, you'll need to bump the version of package.
There are two files that you need to update with the new version you're bumping to:
```sh
setup.py
.bumpversion.cfg
```

As soon as you've bumped your version and pushed your changes, then merge your PR.

Once the PR has been merged, checkout the latest from master then tag and push:
```shell
git checkout master
git pull
git tag X.X.X 
git push --tags
```

