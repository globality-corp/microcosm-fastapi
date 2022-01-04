from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from microcosm_fastapi.conventions.crud_adapter import CRUDStoreAdapter


class EncryptableCRUDStoreAdapter(CRUDStoreAdapter):
    """
    Adapt the CRUD conventions callbacks to the `EncryptableStore` interface.
    """

    async def _update_and_reencrypt(
        self, identifier: UUID, body: BaseModel, session: Optional[AsyncSession] = None
    ):
        """
        Support re-encryption by enforcing that every update triggers a
        new encryption call, even if the the original call does not update
        the encrypted field.
        """
        encrypted_field_name = self.store.model_class.__plaintext__

        current_model = await self.store.retrieve(identifier, session=session)
        current_value = current_model.plaintext

        dict_body = body.dict()

        null_update = (
            # Check if the update is for the encrypted field, and if it's explicitly set to null
            encrypted_field_name in dict_body
            and dict_body.get(encrypted_field_name) is None
        )
        new_value = dict_body.pop(self.store.model_class.__plaintext__, None)
        use_new_value = new_value is not None or null_update

        updated_value = new_value if use_new_value else current_value

        model_kwargs = {
            id: identifier,
            encrypted_field_name: updated_value,
            **dict_body,
        }

        model = self.store.model_class(id=identifier, **model_kwargs)
        return self.store.update(identifier, model, session=session)
