import test_project.daemons.pizza_daemon.handler  # noqa: 401
from microcosm.loaders import (
    load_each,
    load_from_dict,
    load_from_environ,
    load_from_json_file,
)

from microcosm_fastapi.pubsub.daemon import ConsumerDaemonAsync


class PizzaDaemon(ConsumerDaemonAsync):

    @property
    def name(self):
        return "pizza"

    @property
    def loader(self):
        return load_each(
            load_from_dict(self.defaults),
            load_from_environ,
            load_from_json_file,
        )

    @property
    def components(self):
        return super().components + [
            "pizza_daemon_handler",
            # components
            "sns_topic_arns",
        ]


def main():
    daemon = PizzaDaemon()
    daemon.run()
