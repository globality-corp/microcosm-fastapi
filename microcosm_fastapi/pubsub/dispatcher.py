from asyncio import gather
from time import time
from typing import Any, List

from microcosm.api import defaults, typed
from microcosm_logging.decorators import logger
from microcosm_logging.timing import elapsed_time
from microcosm_pubsub.dispatcher import SQSMessageDispatcher
from microcosm_pubsub.result import MessageHandlingResultType

from microcosm_fastapi.pubsub.result import MessageHandlingResultAsync


PUBLISHED_KEY = "X-Request-Published"


@logger
@defaults(
    # Number of failed attempts after which the message stops being processed
    message_max_processing_attempts=typed(int, default_value=None),
    # Quantity of messages to parse within the same runloop
    message_max_concurrent_operations=typed(int, default_value=5),
)
class SQSMessageDispatcherAsync(SQSMessageDispatcher):
    def __init__(self, graph):
        super().__init__(graph)

        self.max_processing_attempts = (
            graph.config.sqs_message_dispatcher_async.message_max_processing_attempts
        )
        self.max_concurrent_operations = (
            graph.config.sqs_message_dispatcher_async.message_max_concurrent_operations
        )

    def handle_batch(self, bound_handlers) -> List[MessageHandlingResultAsync]:
        """
        Send a batch of messages to a function.
        """
        start_time = time()

        instances = []

        # Consume a batch size of messages specified in the configuration. This allows us to get some
        # async speed gains without saturating the local daemon with trying to parse through the
        # entire message queue.
        #
        # We don't anticipate any exceptions from this gather() run because `self.handle_message` already
        # wraps the handler with an exhaustive try/catch
        for message_batch in self.iter_batch(
            self.sqs_consumer.consume(), self.max_concurrent_operations
        ):
            instances += gather(  # type: ignore
                [self.handle_message(message, bound_handlers) for message in message_batch]
            )

        batch_elapsed_time = (time() - start_time) * 1000

        message_batch_size = len(
            [
                instance
                for instance in instances
                if instance.result != MessageHandlingResultType.IGNORED
            ]
        )

        if message_batch_size > 0:
            # NB: Expose formatted message
            message = "Completed batch: Message count: {message_batch_size}, elapsed_time: {batch_elapsed_time}".format(
                message_batch_size=message_batch_size,
                batch_elapsed_time=batch_elapsed_time,
            )
            self.logger.debug(message)

        self.send_batch_metrics(batch_elapsed_time, message_batch_size)

        for instance in instances:
            self.send_metrics(instance)

        return instances

    async def handle_message(self, message, bound_handlers) -> MessageHandlingResultAsync:
        """
        Handle a message.
        """
        with self.opaque.initialize(self.sqs_message_context, message):
            handler = None

            start_handle_time = time()

            with elapsed_time(self.opaque):
                try:
                    self.validate_message(message)
                    handler = self.find_handler(message, bound_handlers)
                    instance = await MessageHandlingResultAsync.invoke(
                        handler=self.wrap_handler(handler),
                        message=message,
                    )
                except Exception as error:
                    instance = MessageHandlingResultAsync.from_error(
                        message=message,
                        error=error,
                    )

            instance.elapsed_time = self.opaque["elapsed_time"]
            published_time = self.opaque.get(PUBLISHED_KEY)
            if published_time:
                instance.handle_start_time = start_handle_time - float(published_time)
            instance.log(
                logger=self.choose_logger(handler),
                opaque=self.opaque,
            )
            instance.error_reporting(
                sentry_config=self.sentry_config,
                opaque=self.opaque,
            )
            instance.resolve(message)
            return instance

    def iter_batch(self, batch: List[Any], k: int):
        for i in range(0, len(batch), k):
            yield batch[i: i + k]


def configure_sqs_message(graph):
    pass
