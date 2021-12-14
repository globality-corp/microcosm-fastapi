from http import HTTPStatus
from typing import Callable, Optional
from uuid import UUID

from fastapi import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDStoreAdapter:
    """
    Adapt the CRUD conventions callbacks to the `Store` interface.
    Does NOT impose transactions; use the `microcosm_postgres.context.transactional` decorator.

    """

    def __init__(self, graph, store):
        self.graph = graph
        self.store = store

    async def _create(self, body: BaseModel, session: Optional[AsyncSession] = None):
        model = self.store.model_class(**body.dict())
        return await self.store.create(model, session=session)

    async def _delete(self, identifier: UUID, session: Optional[AsyncSession] = None):
        await self.store.delete(identifier, session)
        return Response(status_code=HTTPStatus.NO_CONTENT.value)

    async def _replace(
        self, identifier: UUID, body: BaseModel, session: Optional[AsyncSession] = None
    ):
        model = self.store.model_class(id=identifier, **body.dict())
        return await self.store.replace(identifier, model, session=session)

    async def _retrieve(self, identifier: UUID, session: Optional[AsyncSession] = None):
        return await self.store.retrieve(identifier, session=session)

    async def _search(
        self,
        offset: int,
        limit: int,
        link_provider: Callable = None,
        session: Optional[AsyncSession] = None,
        **kwargs,
    ):
        """
        The search endpoint expects to be serialized by
        `microcosm_fastapi.conventions.schemas:SearchSchema`

        You can do this via a route definition that looks like:

        def search(self, offset: int, limit: int) -> SearchSchema(PizzaSchema):
            pass

        """
        items = await self.store.search(offset=offset, limit=limit, session=session, **kwargs)
        count = await self.store.count(session=session, **kwargs)

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
        session: Optional[AsyncSession] = None,
        **kwargs,
    ):
        count = await self.store.count(session=session, **kwargs)
        return count

    async def _update(
        self, identifier: UUID, body: BaseModel, session: Optional[AsyncSession] = None
    ):
        model = self.store.model_class(id=identifier, **body.dict())
        return await self.store.update(identifier, model, session=session)
