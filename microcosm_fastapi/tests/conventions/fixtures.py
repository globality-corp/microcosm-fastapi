from uuid import uuid4
from copy import copy

PERSON_ID_1 = uuid4()
PERSON_ID_2 = uuid4()
PERSON_ID_3 = uuid4()


class Person:
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name


PERSON_1 = Person(PERSON_ID_1, "Alice", "Smith")
PERSON_2 = Person(PERSON_ID_2, "Bob", "Jones")
PERSON_3 = Person(PERSON_ID_3, "Charlie", "Smith")


def person_create(**kwargs):
    return Person(id=PERSON_ID_2, **kwargs)


def person_search(offset, limit):
    return [PERSON_1], 1


def person_update_batch(items):
    return dict(
        items=[
            person_create(**item)
            for item in items
        ]
    )


def person_retrieve(person_id, family_member=None):
    if family_member:
        return PERSON_3
    elif person_id == PERSON_ID_1:
        return PERSON_1
    else:
        return None


def person_delete(person_id):
    return person_id == PERSON_ID_1


def person_delete_batch():
    return True


def person_replace(person_id, **kwargs):
    return Person(id=person_id, **kwargs)


def person_update(person_id, **kwargs):
    if person_id == PERSON_ID_1:
        # Copy to avoid changing attr of constant
        person_1_copy = copy(PERSON_1)
        for key, value in kwargs.items():
            setattr(person_1_copy, key, value)
        return person_1_copy
    else:
        return None

