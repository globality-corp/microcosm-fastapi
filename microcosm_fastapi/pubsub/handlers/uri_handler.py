from abc import ABCMeta
from inspect import iscoroutinefunction

from httpx import get
from microcosm_pubsub.errors import Nack
from microcosm_pubsub.handlers.uri_handler import URIHandler
from requests import codes


class URIHandlerAsync(URIHandler, metaclass=ABCMeta):
    async def __call__(self, message):
        uri = message["uri"]
        self.on_call(message, uri)

        skip_reason = self.get_reason_to_skip(message, uri)
        if skip_reason is not None:
            self.on_skip(message, uri, skip_reason)
            return False

        resource = None

        if iscoroutinefunction(self.get_resource):
            resource = await self.get_resource(message, uri)
        else:
            resource = self.get_resource(message, uri)

        resource = self.convert_resource(resource)

        if await self.handle(message, uri, resource):
            self.on_handle(message, uri, resource)
            return True
        else:
            self.on_ignore(message, uri, resource)
            return False

    async def get_resource(self, message, uri):
        """
        Mock-friendly URI getter.
        Passes message context.
        """
        if self.resource_cache and self.resource_cache_whitelist_callable(
            media_type=message.get("mediaType"), uri=uri
        ):
            response = self.resource_cache.get(uri)
            if response:
                return response

        headers = self.get_headers(message)
        response = await get(uri, headers=headers)
        if response.status_code == codes.not_found and self.nack_if_not_found:
            raise Nack(self.resource_nack_timeout)
        response.raise_for_status()
        response_json = response.json()

        self.validate_changed_field(message, response_json)

        if self.resource_cache and self.resource_cache_whitelist_callable(
            media_type=message.get("mediaType"),
            uri=uri,
        ):
            self.resource_cache.set(uri, response_json, ttl=self.resource_cache_ttl)

        return response_json

    async def handle(self):
        return True
