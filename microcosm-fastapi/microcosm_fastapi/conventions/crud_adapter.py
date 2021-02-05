from microcosm_fastapi.naming import name_for
from typing import Dict, Any, Callable


class CRUDStoreAdapter:
    """
    Adapt the CRUD conventions callbacks to the `Store` interface.
    Does NOT impose transactions; use the `microcosm_postgres.context.transactional` decorator.

    """
    def __init__(self, graph, store):
        self.graph = graph
        self.store = store

    def _create(self, body):
        model = self.store.model_class(**kwargs)
        return self.store.create(model)

    def _delete(self, identifier):
        return self.store.delete(identifier)

    def _replace(self, identifier):
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.replace(identifier, model)

    def _retrieve(self, identifier):
        return self.store.retrieve(identifier)

    async def _search(self, offset, limit, **kwargs):
        items = await self.store.search(offset=offset, limit=limit, **kwargs)
        count = await self.store.count(**kwargs)
        return dict(
            items=items,
            count=count,
        )

    async def _count(self, offset=None, limit=None, **kwargs):
        count = await self.store.count(**kwargs)
        return count

    def _update(self, identifier, body):
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.update(identifier, model)
