from microcosm_fastapi.naming import name_for
from typing import Dict, Any, Callable
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CRUDStoreAdapter:
    """
    Adapt the CRUD conventions callbacks to the `Store` interface.
    Does NOT impose transactions; use the `microcosm_postgres.context.transactional` decorator.

    """
    def __init__(self, graph, store):
        self.graph = graph
        self.store = store

    async def _create(self, body: BaseModel):
        model = self.store.model_class(**body.dict())
        return await self.store.create(model)

    async def _delete(self, identifier: UUID):
        return await self.store.delete(identifier)

    async def _replace(self, identifier: UUID, body: BaseModel):
        model = self.store.model_class(id=identifier, **body.dict())
        return await self.store.replace(identifier, model)

    def _retrieve(self, identifier: UUID):
        return self.store.retrieve(identifier)

    async def _search(self, offset: int, limit: int, **kwargs):
        items = await self.store.search(offset=offset, limit=limit, **kwargs)
        count = await self.store.count(**kwargs)
        return dict(
            items=items,
            count=count,
        )

    async def _count(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs,
    ):
        count = await self.store.count(**kwargs)
        return count

    async def _update(self, identifier, body):
        model = self.store.model_class(id=identifier, **body.dict())
        return self.store.update(identifier, model)
