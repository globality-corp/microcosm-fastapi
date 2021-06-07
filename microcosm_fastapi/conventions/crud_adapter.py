from http import HTTPStatus
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)
from uuid import UUID

from fastapi import Response
from pydantic import BaseModel

from microcosm_fastapi.naming import name_for
from microcosm_fastapi.operations import Operation


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
        await self.store.delete(identifier)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)

    async def _replace(self, identifier: UUID, body: BaseModel):
        model = self.store.model_class(id=identifier, **body.dict())
        return await self.store.replace(identifier, model)

    async def _retrieve(self, identifier: UUID):
        return await self.store.retrieve(identifier)

    async def _search(
        self,
        offset: int,
        limit: int,
        link_provider: Callable = None,
        **kwargs
    ):
        """
        The search endpoint expects to be serialized by
        `microcosm_fastapi.conventions.schemas:SearchSchema`

        You can do this via a route definition that looks like:

        def search(self, offset: int, limit: int) -> SearchSchema(PizzaSchema):
            pass

        """
        items = await self.store.search(offset=offset, limit=limit, **kwargs)
        count = await self.store.count(**kwargs)

        payload = dict(
            items=items,
            count=count,
            offset=offset,
            limit=limit,
        )

        if link_provider:
            payload["_links"] = link_provider(count)

        return payload

    async def _count(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs,
    ):
        count = await self.store.count(**kwargs)
        return count

    async def _update(self, identifier: UUID, body: BaseModel):
        model = self.store.model_class(id=identifier, **body.dict())
        return await self.store.update(identifier, model)
