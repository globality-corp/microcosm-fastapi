from microcosm_daemon.sleep_policy import SleepNow
from microcosm_pubsub.daemon import ConsumerDaemon


class ConsumerDaemonAsync(ConsumerDaemon):
    def process(self):
        """
        Lambda Function method that runs only once
        """
        self.initialize()
        self.graph.logger.info("Local starting daemon {}".format(self.name))
        with self.graph.error_policy:
            self.graph.sqs_message_dispatcher_async.handle_batch(self.bound_handlers)

    def __call__(self, graph):
        """
        Implement daemon by sinking messages from the consumer to a dispatcher function.
        """
        results = graph.sqs_message_dispatcher_async.handle_batch(self.bound_handlers)
        if not results:
            raise SleepNow()

    @property
    def components(self):
        return super().components + [
            "sqs_message_dispatcher_async",
        ]
