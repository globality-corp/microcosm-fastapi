from typing import Optional

from microcosm_postgres.encryption.models import decrypt_instance
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from microcosm_fastapi.database.store import StoreAsync


class EncryptableStoreAsync(StoreAsync):
    """
    A store for (conditionally) encryptable model.
    The store supports delete action for encryptable models by deleting
    the encrypted model.
    Note: in order to use the store, the model must define:
    -  An `encrypted_identifier` property (defaults to `encrypted_id`)
    -  An `encrypted_relationship` property (defaults to `encrypted`)
    """

    def __init__(self, graph, model_class, encrypted_store, **kwargs):
        super().__init__(graph, model_class, **kwargs)
        self.encrypted_store = encrypted_store

    async def delete(self, identifier, session: Optional[AsyncSession] = None):
        instance = await self.retrieve(identifier, session=session)
        result = super().delete(identifier, session=session)
        if instance.encrypted_identifier:
            await self.encrypted_store.delete(instance.encrypted_identifier, session=session)
        return result

    async def update(self, identifier, new_instance, session: Optional[AsyncSession] = None):
        """
        Update an encryptable field, make sure that:
        * We won't change the encryption context key
        * The new value is going to be encrypted
        * The return instance.plaintext is the updated one
        Note: Will expunge the returned instance
        """
        old_instance = await self.retrieve(identifier, session=session)
        old_encrypted_identifier = old_instance.encrypted_identifier

        if (
            new_instance.encryption_context_key
            and old_instance.encryption_context_key != new_instance.encryption_context_key
        ):
            raise ValueError("Cannot change encryption context key")

        # If updating a non encrypted field - skip
        if new_instance.plaintext is None and new_instance.encrypted_relationship is None:
            result = super().update(identifier, new_instance)
            self.expunge(result, session=session)
            return result

        # Verify that the new instance is encrypted if it should be
        # If it's not - encrypt it with the old key
        # If it is - save the expected new plaintext
        if new_instance.plaintext is not None:
            expected_new_plaintext = new_instance.plaintext
            new_instance = self.reencrypt_instance(
                new_instance, old_instance.encryption_context_key
            )
        else:
            decrypt, expected_new_plaintext = decrypt_instance(new_instance)

        result = super().update(identifier, new_instance, session=session)

        # Delete the old encrypted value (instead of using sqlalchemy cascade)
        if old_encrypted_identifier != new_instance.encrypted_identifier:
            await self.encrypted_store.delete(old_encrypted_identifier, session=session)

        # Update the return result, super().update() won't do it.
        self.expunge(result, session=session)
        result.plaintext = expected_new_plaintext
        return result

    def reencrypt_instance(self, instance, encryption_context_key):
        mapper = inspect(self.model_class)
        values = {
            key: value
            for key, value in instance.__dict__.items()
            if key in mapper.c
        }
        values[self.model_class.__encryption_context_key__] = encryption_context_key
        return self.model_class(**values)

    async def search_encrypted_ids(self, context_id, session: Optional[AsyncSession] = None):
        async with self.with_maybe_session(session) as session:
            query = select(self.model_class.id).where(
                getattr(self.model_class, self.model_class.__encrypted_identifier__)
                != None,  # noqa
                getattr(self.model_class, self.model_class.__encryption_context_key__)
                == context_id,
            )
            results = await session.execute(query)

        return [response[0] for response in results.all()]
