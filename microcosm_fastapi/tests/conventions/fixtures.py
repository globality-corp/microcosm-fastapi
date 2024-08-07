from copy import copy
from uuid import UUID, uuid4

from microcosm_postgres.errors import ModelNotFoundError

from microcosm_fastapi.conventions.schemas import BaseSchema, SearchSchema


PERSON_ID_1 = uuid4()
PERSON_ID_2 = uuid4()
PERSON_ID_3 = uuid4()


class Person:
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return dict(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
        )


PERSON_1 = Person(PERSON_ID_1, "Alice", "Smith")
PERSON_2 = Person(PERSON_ID_2, "Bob", "Jones")
PERSON_3 = Person(PERSON_ID_3, "Charlie", "Smith")


class NewPersonSchema(BaseSchema):
    first_name: str
    last_name: str


class PersonSchema(NewPersonSchema):
    id: UUID


class UpdatePersonSchema(BaseSchema):
    first_name: str | None
    last_name: str | None


async def person_create(body: NewPersonSchema) -> PersonSchema:
    return Person(id=PERSON_ID_2, **body.dict()).to_dict()


async def person_search(offset: int = 0, limit: int = 20) -> SearchSchema(PersonSchema):  # type: ignore

    payload = dict(
        items=[PERSON_1],
        count=1,
        offset=offset,
        limit=limit,
    )
    return payload


async def person_retrieve(person_id: UUID) -> PersonSchema:
    if person_id == PERSON_ID_1:
        return PERSON_1.to_dict()
    else:
        raise ModelNotFoundError(
            "{} not found".format(
                Person.__name__,
            ),
        )


async def person_delete(person_id: UUID):
    return person_id == PERSON_ID_1


async def person_update(person_id: UUID, body: UpdatePersonSchema) -> PersonSchema:
    if person_id == PERSON_ID_1:
        person_1_copy = copy(PERSON_1)
        for key, value in body.dict().items():
            if value is None:
                continue
            setattr(person_1_copy, key, value)
        return person_1_copy.to_dict()
    else:
        raise ModelNotFoundError(
            "{} not found".format(
                Person.__name__,
            ),
        )
