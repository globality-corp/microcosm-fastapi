from abc import ABCMeta, abstractmethod

from microcosm_pubsub.chain import Chain

from microcosm_fastapi.pubsub.handlers.uri_handler import URIHandlerAsync


class ChainHandlerAsync(metaclass=ABCMeta):
    """
    Resolve a chain on call. Pass to the chain the message to the chain.
    """

    @abstractmethod
    def get_chain(self):
        pass

    async def __call__(self, message):
        return await Chain(self.get_chain())(message=message)


class ChainURIHandlerAsync(URIHandlerAsync, metaclass=ABCMeta):
    """
    Base handler for URI-driven events based on URIHandler
    Resolve a chain on handle.
    Pass to the chain the message and the fetched resource.
    """

    @abstractmethod
    def get_chain(self):
        pass

    @property
    def resource_name(self):
        return "resource"

    async def handle(self, message, uri, resource):
        kwargs = dict(
            message=message,
            uri=uri,
        )
        kwargs[self.resource_name] = resource
        chain = self.get_chain()
        await chain(**kwargs)

        return True
