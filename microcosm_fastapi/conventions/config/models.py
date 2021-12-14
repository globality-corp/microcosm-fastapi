from json import dumps, loads
from typing import Any, Dict

from microcosm.loaders.compose import PartitioningLoader


class Config:
    """
    Wrapper around service config state.
    """

    def __init__(self, graph, include_build_info=True):
        self.graph = graph
        self.name = graph.metadata.name

    def to_dict(self) -> Dict[str, Any]:
        """
        Encode the name, the status of all checks, and the current overall status.
        """
        if not isinstance(self.graph.loader, PartitioningLoader):
            return dict(msg="Config sharing disabled for non-partioned loader")

        if not hasattr(self.graph.loader, "secrets"):
            return dict(msg="Config sharing disabled if no secrets are labelled")

        def remove_nulls(dct):
            return {
                key: value
                for key, value in dct.items()
                if value is not None
            }

        return loads(
            dumps(self.graph.loader.config, skipkeys=True, default=lambda obj: None),
            object_hook=remove_nulls,
        )
